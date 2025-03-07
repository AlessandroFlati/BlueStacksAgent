import queue
import threading

import cv2
import numpy as np

from BlueStacksAgent import Agent
from BlueStacksAgent.actuators.base import BaseActuator
from BlueStacksAgent.agents import ScrcpyAgent

# Create a thread-safe queue for frames
frame_queue = queue.Queue(maxsize=2)


class SimpleActuator(BaseActuator):
    def __init__(self, frame_queue):
        super().__init__()
        self.window_name = "Simple Actuator"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.frame_queue = frame_queue

    def process(self, frames: np.ndarray):
        # Get the latest frame from the frames array
        frame = frames[-1]
        if frame is not None:
            # Push the frame to the queue for the main thread to display
            self.frame_queue.put(frame)


def display_loop():
    """This loop runs on the main thread and handles the GUI display."""
    current_resolution = None
    while True:
        # Try to retrieve a frame from the queue without blocking too long
        try:
            frame = frame_queue.get(timeout=0.1)
            # Resize the window to fit the frame
            cv2.imshow("Simple Actuator", frame)
            if current_resolution is None or frame.shape[:2] != current_resolution:
                print(f"Resizing window to {frame.shape[0] // 2} x {frame.shape[1] // 2}")
                current_resolution = frame.shape[:2]
                cv2.resizeWindow("Simple Actuator", frame.shape[1] // 2, frame.shape[0] // 2)
        except queue.Empty:
            pass  # No frame to display; continue

        # Check for the 'q' key to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


# Create and configure the BlueStacksAgent
# (Ensure the adb device is set up correctly)
scrcpy_agent = ScrcpyAgent(adb_port=5556)
simple_actuator = SimpleActuator(frame_queue)
bluestacks_agent = Agent(stream_agent=scrcpy_agent, actuator=simple_actuator)

# Start the agent in a background thread
agent_thread = threading.Thread(target=bluestacks_agent.start)
agent_thread.daemon = True  # Allows the program to exit even if the thread is still running
agent_thread.start()

# Run the display loop on the main thread
display_loop()

# When the display loop is exited (e.g., by pressing 'q'), stop the agent
bluestacks_agent.stop()
agent_thread.join()
