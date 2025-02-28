import time
from collections import deque
from threading import Thread

import numpy as np

from BlueStacksAgent.actuators.base import BaseActuator
from BlueStacksAgent.agents.base import BaseAgent


class BlueStacksAgent:
    """
    BlueStacksAgent ties together a screen capture agent (e.g., scrcpy, minicap, or mediaprojection)
    and an actuator that processes captured frames.

    This class instantiates the proper capture agent based on a provided stream type and registers
    an actuator to process each frame.
    """

    def __init__(self, stream_agent: BaseAgent = None, actuator: BaseActuator = None, **kwargs):
        """
        :param stream_agent: An instance of a subclass of BaseAgent that implements start_stream(callback).
        :param actuator: An instance of a subclass of BaseActuator that implements on_frame(frame).
        :param kwargs: Additional keyword arguments passed to the underlying capture agent's constructor.
        """
        if stream_agent is None:
            raise ValueError("stream_agent must be provided.")
        if actuator is None:
            raise ValueError("actuator must be provided.")

        self.stream_agent: BaseAgent = stream_agent
        self.actuator: BaseActuator = actuator
        self._error = None
        self.thread = None
        self.error_thread = None
        self.is_processing = False

    def _process_loop(self):
        """
        Continuously processes frames from the stream agent.
        :return:
        """
        while self.is_processing:
            self._error = None
            if self.stream_agent.frame_buffer:
                frames = self._convert_to_3d_array(self.stream_agent.frame_buffer)
                try:
                    if frames.shape[0] > 0:
                        self.actuator.process(frames)
                except Exception as e:
                    self._error = e
                    break
            else:
                time.sleep(0.1)

    def _error_loop(self):
        """
        Continuously checks for errors in the processing loop.
        :return:
        """
        while self.is_processing:
            if self._error:
                print(f"Error in processing loop: {self._error}")
                self.thread.join()
                break
            time.sleep(0.1)

    def start(self):
        """
        Start the capture stream and processing loop.
        """
        self.is_processing = True
        self.thread = Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        self.error_thread = Thread(target=self._error_loop, daemon=True)
        self.error_thread.start()
        self.stream_agent.start_stream()

    def stop(self):
        """
        Stop the capture stream.
        """
        self.is_processing = False
        self.stream_agent.stop_stream()
        if self.thread:
            self.thread.join()
        if self.error_thread:
            self.error_thread.join()

    @staticmethod
    def _convert_to_3d_array(frame_buffer: deque) -> np.ndarray:
        """
        Convert the frame buffer to a 3D NumPy array.
        :param frame_buffer: A deque of frames.
        :return: A 3D NumPy array of frames.
        """
        frame_buffer_copy = frame_buffer.copy()
        return np.array([f for f in frame_buffer_copy if f is not None])
