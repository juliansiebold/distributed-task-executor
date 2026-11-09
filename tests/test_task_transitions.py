from itertools import product
from uuid import uuid4

import pytest
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from distributed_task_executor.core.models import Task, TaskPayload, TaskStatus
from distributed_task_executor.core.task_state import (
    DeadLetterState,
    FailedState,
    PendingState,
    RunningState,
    SucceededState,
    TaskException,
)

PENDING = TaskStatus.PENDING
RUNNING = TaskStatus.RUNNING
FAILED = TaskStatus.FAILED
SUCCEEDED = TaskStatus.SUCCEEDED
DEAD_LETTER = TaskStatus.DEAD_LETTER

STATES = {
    PENDING: PendingState,
    RUNNING: RunningState,
    FAILED: FailedState,
    SUCCEEDED: SucceededState,
    DEAD_LETTER: DeadLetterState,
}
ACTIONS = ["start", "succeed", "fail", "retry", "dead_letter"]
RETRIES_LEFT = True
NO_RETRIES_LEFT = False

# Every allowed transition, as (state, action, Retries left?) -> next state.
# Every combination missing from this table must raise TaskException.
TRANSITIONS = {
    (PENDING, "start", RETRIES_LEFT): RUNNING,
    (PENDING, "start", NO_RETRIES_LEFT): RUNNING,
    (RUNNING, "succeed", RETRIES_LEFT): SUCCEEDED,
    (RUNNING, "succeed", NO_RETRIES_LEFT): SUCCEEDED,
    (RUNNING, "fail", RETRIES_LEFT): FAILED,
    (RUNNING, "fail", NO_RETRIES_LEFT): FAILED,
    (FAILED, "retry", RETRIES_LEFT): PENDING,
    (FAILED, "dead_letter", NO_RETRIES_LEFT): DEAD_LETTER,
}
REFUSED = sorted(
    set(product(STATES, ACTIONS, [RETRIES_LEFT, NO_RETRIES_LEFT])) - set(TRANSITIONS),
    key=str)


def rehydrated_task(status: TaskStatus, retry_count: int, retry_limit: int) -> Task:
    return Task.rehydrate(
        state=STATES[status](),
        task_id=uuid4(),
        payload=TaskPayload(delay_seconds=1),
        client_id="test-client",
        retry_count=retry_count,
        retry_limit=retry_limit)


def task_in(status: TaskStatus, retries_left: bool) -> Task:
    return rehydrated_task(status, retry_count=2 if retries_left else 3, retry_limit=3)


def perform(task: Task, action: str) -> None:
    getattr(task, action)()


def case_id(case: tuple) -> str:
    status, action, retries_left = case
    return f"{status}-{action}-{'retries left' if retries_left else 'no retries left'}"


@pytest.mark.parametrize("case", TRANSITIONS, ids=case_id)
def test_allowed_action_moves_the_task_to_its_next_state(case):
    status, action, retries_left = case
    task = task_in(status, retries_left)

    perform(task, action)

    assert task.state.status == TRANSITIONS[case]


@pytest.mark.parametrize("case", REFUSED, ids=case_id)
def test_any_other_action_is_refused_and_changes_nothing(case):
    status, action, retries_left = case
    task = task_in(status, retries_left)
    retry_count = task.retry_count

    with pytest.raises(TaskException) as error:
        perform(task, action)

    assert error.value.failed_task is task
    assert task.state.status == status
    assert task.retry_count == retry_count


def test_retry_count_increases_when_a_failed_task_returns_to_pending():
    task = rehydrated_task(FAILED, retry_count=2, retry_limit=3)

    task.retry()

    assert task.retry_count == 3


@pytest.mark.parametrize(
    "case",
    [case for case in TRANSITIONS if case[:2] != (FAILED, "retry")],
    ids=case_id)
def test_retry_count_stays_the_same_on_every_other_transition(case):
    status, action, retries_left = case
    task = task_in(status, retries_left)
    retry_count = task.retry_count

    perform(task, action)

    assert task.retry_count == retry_count


def test_retry_limit_of_zero_sends_the_first_failure_to_dead_letter():
    task = Task(payload=TaskPayload(delay_seconds=1), client_id="test-client", retry_limit=0)
    task.start()
    task.fail()

    with pytest.raises(TaskException):
        task.retry()
    assert task.state.status == FAILED
    assert task.retry_count == 0

    task.dead_letter()

    assert task.state.status == DEAD_LETTER
    assert task.retry_count == 0


# With every action equally likely, most sequences reach Succeeded early and rarely
# use up the Retries, which let a Retry past the Retry limit go unnoticed in 4 of 12 runs.
ACTIONS_FAVOURING_RETRIES = ACTIONS + ["start", "fail", "retry"] * 3


class TaskLifecycle(RuleBasedStateMachine):
    """Runs random action sequences against a Task and tracks what should happen."""

    @initialize(retry_limit=st.integers(min_value=0, max_value=10))
    def create_task(self, retry_limit):
        self.task = Task(
            payload=TaskPayload(delay_seconds=1),
            client_id="test-client",
            retry_limit=retry_limit)
        self.task_id = self.task.task_id
        self.retry_limit = retry_limit
        self.expected_status = PENDING
        self.expected_retry_count = 0

    @rule(action=st.sampled_from(ACTIONS_FAVOURING_RETRIES))
    def perform_action(self, action):
        retries_left = self.expected_retry_count < self.retry_limit
        next_status = TRANSITIONS.get((self.expected_status, action, retries_left))

        if next_status is None:
            with pytest.raises(TaskException):
                perform(self.task, action)
            return

        perform(self.task, action)
        if (self.expected_status, next_status) == (FAILED, PENDING):
            self.expected_retry_count += 1
        self.expected_status = next_status

    @invariant()
    def task_matches_what_should_have_happened(self):
        assert self.task.state.status == self.expected_status
        assert self.task.retry_count == self.expected_retry_count

    @invariant()
    def retry_count_stays_within_retry_limit(self):
        assert 0 <= self.task.retry_count <= self.task.retry_limit

    @invariant()
    def task_id_and_retry_limit_never_change(self):
        assert self.task.task_id == self.task_id
        assert self.task.retry_limit == self.retry_limit


TestTaskLifecycle = TaskLifecycle.TestCase
