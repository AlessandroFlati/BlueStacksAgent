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
        self._callback = self._create_callback()

    def _create_callback(self):
        """
        Creates a callback function to process captured frames.
        It simply forwards each frame to the actuator's on_frame method.
        """

        def callback(frame):
            if self.actuator:
                self.actuator.on_frame(frame)

        return callback

    def start(self):
        """
        Start the capture stream with the attached callback.
        """
        self.stream_agent.start_stream(self._callback)

    def stop(self):
        """
        Stop the capture stream.
        """
        self.stream_agent.stop_stream()
