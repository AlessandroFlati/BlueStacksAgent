import pytest
import time
from BlueStacksAgent.agents.scrcpy_agent import ScrcpyAgent

# Dummy scrcpy agent that overrides the streaming loop to simulate a frame callback.
class DummyScrcpyAgent(ScrcpyAgent):
    def _stream_loop(self):
        # Instead of starting a real scrcpy client, immediately invoke the callback.
        if self.callback:
            self.callback("dummy_frame")
        self._is_streaming = False

# Fixture for the dummy scrcpy agent.
@pytest.fixture
def dummy_scrcpy_agent():
    return DummyScrcpyAgent()

def test_scrcpy_agent_start_stop(dummy_scrcpy_agent):
    frames = []
    def dummy_callback(frame):
        frames.append(frame)
    dummy_scrcpy_agent.start_stream(dummy_callback)
    # Allow some time for the dummy stream to simulate frame delivery.
    time.sleep(0.2)
    dummy_scrcpy_agent.stop_stream()
    assert "dummy_frame" in frames
