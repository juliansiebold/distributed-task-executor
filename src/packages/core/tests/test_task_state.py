import pytest

from ..task_state import PendingState, RunningState, SuccessState, FailedState
from ..models import Task, TaskPayload

@pytest.fixture
def test_payload():
    return TaskPayload(caller='TestCaller', delay_seconds=1)

class TestPendingState:

    def test_init_running_transition(self, test_payload):

        test_init_task = Task(payload=test_payload, state=PendingState())
        test_init_task.start()

        assert isinstance(test_init_task.state, RunningState)

# TODO create Task object for testing

# happy case running -> Success
# Happy Case move init -> Running -> Failed
# Expected fail Running -> init
# Expected fail Success -> Running
# Expected fail Failed -> Running
