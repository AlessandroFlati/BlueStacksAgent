# BlueStacksAgent
A framework for integrating with BlueStacks istances under Windows for fast FPS video processing and decision-making.

## Purpose
This aims to be a Python library that seamlessly integrates with a running BlueStacks Android emulator, providing real-time screen capture and interactive control. The library will capture video frames at near native device resolution (and frame rate) without heavy recording overhead, feed them into user-defined processing callbacks, and allow simulated input (taps, swipes, etc.) via ADB with randomness to avoid detection. The design will be modular for easy customization and future extension.

## Limitations
For now, only Windows OS is supported. 

Using Android Debug Bridge (ADB) to capture screenshots in a loop is straightforward and preserves the device’s full native resolution. However, ADB-based capture has a performance ceiling of around 150 ms per frame on BlueStacks (approximately 6–7 FPS). Some optimizations, like compressing the output (e.g. using `adb exec-out "screencap | gzip -1"`) can improve throughput by reducing data size, but ADB will not easily achieve high framerates due to bandwidth limits.

## Explanation

Three interfaces will be provided for processing video frames:
- **Scrcpy**: A popular open-source project that mirrors Android devices to a PC screen and provides a low-latency, high-frame-rate stream. Scrcpy is a good choice for real-time video processing, but it requires a separate process to run.
- **Minicap**: A lightweight, high-performance screen capture tool that can be used to capture video frames at high framerates. Minicap is a good choice for high-speed video processing as well, but it requires a separate process to run.
- **MediaProjection**: An Android API that allows apps to capture the device screen at high framerates. MediaProjection is a good choice for high-speed video processing, but it requires an app to be installed on the device.

### Scrcpy

#### Setup

1. **Enable ADB for BlueStacks**: Ensure BlueStacks is running with ADB enabled. In BlueStacks settings or via command, allow debugging and connect to it using ADB (e.g. adb connect localhost:5555 on Windows). Verify the BlueStacks instance is listed by adb devices.
2. **Install Scrcpy on PC**: Download and install scrcpy on the Windows host. Make sure the scrcpy executable (and adb if not already in PATH) is accessible from Python (add to PATH).
3. **Optimize Scrcpy Settings**: You can adjust scrcpy parameters to balance quality and performance. For example, limit resolution (--max-size 1280) or bitrate (--bit-rate 4M) to reduce bandwidth, or set max FPS (--max-fps 30) to stabilize frame rate. By default scrcpy uses the device’s full resolution and an 8 Mbps H.264 stream, which offers low latency and high FPS in most cases. 
H.264 is recommended over H.265 for lower latency
4. **Test Scrcpy Mirror**: Run scrcpy from a command prompt to ensure it can mirror the BlueStacks screen in a window. This also confirms ADB connectivity and that the scrcpy server can run on the Android side.

#### Optimization strategies
- **Use Hardware Encoding**: Scrcpy by default leverages the Android device’s hardware H.264 encoder, which is efficient. This keeps CPU usage low and latency small on the device side. Ensure H.264 is used (the default) as it provides lower latency than H.265. Tune Bitrate and Resolution: For BlueStacks, you can experiment with scrcpy options. A higher bitrate (e.g. 16M) can improve quality at the cost of slightly more bandwidth. Reducing resolution (--max-size) can lower latency if the encoding or decoding becomes a bottleneck at full HD. There’s a trade-off: lower resolution means less data per frame (faster to encode/transmit) but also less detail. Choose the lowest resolution that still meets your accuracy needs.
- **Frame Rate Capping**: If maximum real-time speed is not required, capping the frame rate (using --max-fps) can reduce CPU/GPU load on both sides, which might improve stability and reduce latency spikes. For instance, limiting to 30 FPS ensures the system isn’t overtaxed trying to hit 60 FPS.
- **Asynchronous Processing**: In Python, handle frames on a separate thread or queue to avoid blocking the network loop. The `scrcpy_client.start(threaded=True)` already does this – it runs the capture in a separate thread. Your on_frame callback should also be efficient; if heavy processing is needed, consider offloading it to another thread or process. This prevents backlog – scrcpy will drop or skip frames if the client can’t keep up, ensuring you always get the most recent frame with minimal delay (rather than buffering outdated frames).
- **Low-Latency Decoding**: Decoding H.264 in Python (via `scrcpy-client`) is usually fast, but for further optimization you could use OpenCV’s VideoCapture or GPU decoding if available. With scrcpy-client, frames are delivered ready-to-use, so just ensure your Python environment can handle the data quickly (use NumPy operations or vectorized code for efficiency).

### Minicap

#### Setup
1. **Obtain Minicap Binaries**: Download the Minicap binary and its companion .so library for the Android version and CPU architecture that BlueStacks uses. (Minicap provides pre-built binaries for various Android API levels and ABIs in the openSTF repository. BlueStacks 5, for example, might emulate Android 7.1.2 (API 25) on x86 or x86_64 – use `adb shell getprop ro.build.version.sdk` and `ro.product.cpu.abi` to identify the correct build.)
2. **Deploy to BlueStacks**: Push the minicap executable and matching minicap.so to the device, typically to `/data/local/tmp/`:
    ```bash
    adb push minicap /data/local/tmp/
    adb push minicap.so /data/local/tmp/
    ```
   Ensure both files are in /data/local/tmp and set executable permission on minicap (adb shell chmod 755 /data/local/tmp/minicap).
3. **Run Minicap**: Execute minicap on BlueStacks with the correct parameters. You must specify the device’s real screen size, desired output size, and orientation in the `-P` argument. For example, if the BlueStacks display is 1080x1920 and you want full resolution output in portrait:
   ```bash
   adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x1920@1080x1920/0 &
   ```
    This command starts minicap in the background, capturing frames at 1080x1920 and outputting them at the same resolution in portrait mode. The `&` at the end runs minicap in the background so you can continue using the shell. Here we used the full resolution for both real and virtual size, and 0 for the rotation (portrait). Minicap will print `OK` if it starts successfully.
4. **Forward the Minicap Socket**: Minicap listens on a local abstract socket named minicap by default. Forward this to a TCP port on the host so that Python can connect. For example:
   ```bash
   adb forward tcp:1313 localabstract:minicap
   ```
   This maps the device’s minicap stream to localhost:1313 on your PC. (Use any free port if 1313 is taken.)

#### Optimization strategies
- **Adjust Output Size**: If full resolution is not needed, you can set a smaller virtual size in the -P parameter (e.g. 1080x1920@540x960/0 for half resolution). This reduces the pixel data to encode, increasing frame rate and reducing latency. BlueStacks will then downscale the image before sending.
- **JPEG Compression Overhead**: Minicap’s JPEG compression is fast (using libjpeg-turbo), but it still adds latency per frame. To optimize, ensure BlueStacks has sufficient CPU allocated. If you observe high latency, consider lowering the JPEG quality or resolution. (Minicap doesn’t offer a command-line for quality, but it’s tuned for a good balance by default.) In extreme cases, a lower bit-depth or grayscale stream (not directly supported by minicap out of the box) could speed up encoding, but that would require modifying minicap’s source.
- **Frame Skipping**: On the Python side, if you cannot process frames as fast as they arrive, you might accumulate latency. To prevent this, you can drop frames when behind. For example, always read the latest frame and discard older ones. Minicap’s protocol doesn’t natively support jumping frames, but you can achieve a similar effect by reading from the socket and only decoding the most recent frame available. One strategy is to use a separate thread to continuously read frames into a single volatile buffer (overwriting old frames if not yet processed by the main thread). This way, your processing thread always gets the newest frame. The QUIRK_DUMB flag in minicap’s banner indicates it will even send duplicate frames if nothing changed – so dropping some won’t break continuity.
- **Networking Considerations**: Since BlueStacks is on the same host, the ADB forwarding goes over the loopback interface – which is very fast (much faster than USB). Ensure you use adb connect 127.0.0.1 (or the given port) for a direct connection. Avoid running other heavy ADB transfers concurrently, as USB/ADB bandwidth is finite (minicap frames are already quite large). Also, only one client can connect to minicap at a time, so use a single socket and share the frames as needed in your app.
- **Parallel Decoding**: If using a high frame rate, JPEG decoding on the Python side could become a bottleneck. You can offload decoding to multiple threads or use hardware-accelerated JPEG decode if available. However, OpenCV’s imdecode is usually fast enough for 1080p at 30fps on modern CPUs. Monitor your CPU usage; if decoding is maxing out one core, consider using a thread pool where each thread decodes a frame (though be mindful of thread synchronization on the socket read).

### MediaProjection

#### Setup
1. **Develop a Capture App**: Create a minimal Android app (using Android Studio or similar) that utilizes the MediaProjection API to capture the screen. This app will run inside BlueStacks. Give it a service or activity that can start on boot or via a manual launch. Since MediaProjection requires user consent, the app should prompt for permission to capture the screen on startup (using MediaProjectionManager.createScreenCaptureIntent()). You’ll need to accept this dialog in BlueStacks (it will pop up asking to allow screen capture).
2. **Implement Screen Capture**: Once permission is granted, use the MediaProjection to create a VirtualDisplay with full screen dimensions. There are two main approaches:
   - **(a) ImageReader + Bitmap Streaming**: Attach an ImageReader to the VirtualDisplay’s surface to receive frame buffers. On each frame (`ImageReader.OnImageAvailable` callback), acquire the latest image and convert it to a Bitmap or JPEG byte array. Then send this over a socket. This approach essentially mirrors what minicap does, but using the official API. It’s straightforward: you get raw pixel data for each frame which you can compress to JPEG/PNG. A Stack Overflow example achieved this by “creating bitmap of your screen by MediaProjection API … now send the stream of bitmaps using Socket”.
   - **(b) MediaCodec (Hardware Encoder) Streaming**: For higher performance, create a MediaCodec encoder for video/AVC. Obtain an input Surface from the encoder (`MediaCodec.createInputSurface()`) and supply that to `MediaProjection.createVirtualDisplay(...)`. Now the screen images are fed directly into the video encoder. Configure the encoder for a high bitrate (e.g. 8Mbps) and desired frame rate (30 or 60). As the encoder produces output H.264 frames, packetize them (e.g. into an MP4 or MPEG-TS stream) and send over a socket. This is essentially what scrcpy’s server does internally. It avoids the overhead of per-frame JPEG compression by leveraging efficient video encoding, potentially yielding lower latency for high FPS. The trade-off is that you must decode the video on the PC side.
3. **Set Up Data Transmission**: In the app, open a communication channel to the host. The simplest method is a TCP socket. For instance, open a ServerSocket on the Android side (listening on port, say, 1717) and when the host connects, start sending frames. Alternatively, use an Android LocalSocket (on localhost) and rely on adb forward like we did for minicap. For simplicity, you can use adb forward tcp:1717 tcp:1717 and have the app listen on 127.0.0.1:1717. This way, no firewall or network config is needed – ADB will tunnel the data.
4. **Build and Install**: Compile the app and install it in BlueStacks (adb install yourApp.apk). Launch the app in BlueStacks and grant the screen capture permission. You should see the app start streaming (perhaps indicate status with a notification or log).
5. **Connect from Python**: On the host, after forwarding the port, your Python client can connect to localhost:1717 (or whichever port you chose) to receive the data.

#### Optimization strategies
- **Acquire Latest Frame**: If using the ImageReader method, always acquire and discard older frames quickly. Use ImageReader.acquireLatestImage() in the callback, which gives you the most recent frame and drops any pending ones you didn’t process. This ensures you don’t build up lag if the PC side is briefly slow – you’ll always snap to the newest frame. The slight downside is you may skip some intermediate frames (reducing effective FPS during slowdowns), but it keeps latency minimal for real-time needs.
- **Compression Choices**: JPEG is a good default for simplicity, but you can tune quality. For example, if you implement compression with Android’s Bitmap.compress(), you could choose Bitmap.CompressFormat.JPEG with 80-90% quality for a good trade-off. PNG would be lossless in terms of image quality but is slower and yields larger files – not ideal for real-time. If absolute pixel perfection is not required, JPEG at high quality is virtually indistinguishable and much faster.
- **Video Encoding for Efficiency**: If you used the MediaCodec approach, set it to use low-latency configurations: e.g., a small GOP (Group of Pictures) size or all I-frames. By default, an H.264 encoder might emit an I-frame every 1-2 seconds and use predicted frames (P-frames) in between. While that drastically reduces bitrate, it means the decoder might depend on previous frames (which could add latency if a frame is lost or delayed). For lowest latency, you can request an IDR-frame very frequently (even every frame, which essentially makes it MJPEG in an H.264 container). This increases data size but makes each frame independent. Many encoders allow setting KEY_I_FRAME_INTERVAL to 1 (every frame is a key frame) or a small number. Also consider using MediaCodec.setParameters() with BITRATE_MODE_CQ (constant quality) or other flags if supported, to reduce any buffering the encoder might do.
- **Threading and Buffers (Android side)**: Ensure the socket writing is on a separate thread from the capture. For example, you might have the ImageReader callback quickly copy the pixel data into a queue and then a socket thread that compresses (if needed) and sends it. This way, capturing isn’t blocked by network delays. If using MediaCodec, the encoding runs in its own thread internally, but you should quickly dequeue output buffers and send them off so the encoder doesn’t block.
- **Networking and Transfer**: Over localhost/ADB, you won’t face typical network latency, but you are limited by ADB’s throughput. If you find that to be a bottleneck, an alternative is to have the app open a direct socket to the host machine’s IP (since BlueStacks is an emulator, 10.0.2.2 usually refers to the host). You could bypass ADB and send via a typical TCP socket to host:port. However, this adds complexity (firewall, needing the host IP, etc.). In most cases, ADB forward is sufficient and quite fast for this use-case.
- **Resource Management**: BlueStacks is sharing your PC’s resources. To keep latency low, run BlueStacks in high performance mode and allocate ample CPU cores/RAM to it (as allowed by BlueStacks settings). The capture app should release the Image objects promptly (image.close() after using it) to avoid memory leaks, and stop the projection properly when done (mediaProjection.stop()), so that the virtual display doesn’t continue consuming resources in background.

## Usage
TBD

## References
- [Scrcpy]TBD
- [Minicap]TBD
- [MediaProjection]TBD
- [ADB]TBD
- [BlueStacks]TBD
- [Android]TBD

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
