import abc

import pytest
from BlueStacksAgent.actuators.base import BaseActuator

# Dummy actuator implementing BaseActuator
class DummyActuator(BaseActuator):
    def __init__(self):
        self.frames = []
    def on_frame(self, frame):
        self.frames.append(frame)

# Fixture for reuse in other tests
@pytest.fixture
def dummy_actuator():
    return DummyActuator()

def test_dummy_actuator_on_frame(dummy_actuator):
    # Test that on_frame properly collects frames.
    frame = "test_frame"
    dummy_actuator.on_frame(frame)
    assert dummy_actuator.frames == ["test_frame"]

def test_base_actuator_instantiation_error():
    # Attempting to instantiate BaseActuator should raise a TypeError.
    with pytest.raises(TypeError):
        BaseActuator()

def test_base_actuator_not_implemented():
    # Attempting to instantiate BaseActuator should raise a TypeError.
    class NotImplActuator(BaseActuator):
        pass
    with pytest.raises(TypeError):
        NotImplActuator()
