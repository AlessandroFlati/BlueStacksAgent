import pytest

from BlueStacksAgent.actuators.base import BaseActuator
from BlueStacksAgent.agents import BaseAgent
from BlueStacksAgent.bluestacks_agent import BlueStacksAgent


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


class DummyStreamAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.callback = None

    def start_stream(self, callback):
        self.callback = callback

    def stop_stream(self):
        self.callback = None


# Fixture for the dummy stream agent.
@pytest.fixture
def dummy_stream_agent():
    return DummyStreamAgent()


# Dummy BlueStacksAgent that overrides the start method to simulate a frame callback.
class DummyBlueStacksAgent(BlueStacksAgent):
    pass


def test_bluestacks_agent_start_stop(dummy_stream_agent, dummy_actuator):
    agent = DummyBlueStacksAgent(dummy_stream_agent, dummy_actuator)
    agent.start()
    # Allow some time for the dummy stream to simulate frame delivery.
    agent.actuator.on_frame("dummy_frame")
    assert "dummy_frame" in dummy_actuator.frames
    agent.stop()
    assert not agent.stream_agent.is_streaming()


def test_bluestacks_agent_instantiation_error(dummy_stream_agent, dummy_actuator):
    # Attempting to instantiate BlueStacksAgent without a stream_agent should raise a ValueError.
    with pytest.raises(ValueError):
        BlueStacksAgent(actuator=dummy_actuator)

    # Attempting to instantiate BlueStacksAgent without an actuator should raise a ValueError.
    with pytest.raises(ValueError):
        BlueStacksAgent(stream_agent=dummy_stream_agent)

def test_callback(dummy_stream_agent, dummy_actuator):
    agent = BlueStacksAgent(dummy_stream_agent, dummy_actuator)
    agent.start()
    # Allow some time for the dummy stream to simulate frame delivery.
    agent.actuator.on_frame("dummy_frame")
    assert "dummy_frame" in dummy_actuator.frames
    agent.stop()
    assert not agent.stream_agent.is_streaming()
