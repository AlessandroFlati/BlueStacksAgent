import abc

import numpy as np


class BaseActuator(abc.ABC):
    """
    Abstract class for actuators that work with BlueStacksAgent.
    The process method must be implemented by any subclass to process frames.
    """

    @abc.abstractmethod
    def process(self, frames: np.ndarray):
        """
        Callback function to process a captured frame.
        :param frames: The buffer of captured frames (i.e., a 3D NumPy array, where the first dimension
                       represents the frame index, and the remaining dimensions represent the frame data).
        """
