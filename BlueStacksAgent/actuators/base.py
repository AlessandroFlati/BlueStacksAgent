import abc

class BaseActuator(abc.ABC):
    """
    Semi-abstract class for actuators that work with BlueStacksAgent.
    The on_frame method must be implemented by any subclass to process frames.
    """

    @abc.abstractmethod
    def on_frame(self, frame):
        """
        Callback function to process a captured frame.
        :param frame: The captured frame (e.g., a NumPy array).
        """
