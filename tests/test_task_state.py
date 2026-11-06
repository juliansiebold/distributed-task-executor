import pytest
from pydantic import ValidationError

from distributed_task_executor.core.models import Task, TaskPayload, TaskStatus
from distributed_task_executor.core.task_state import PendingState, TaskException


@pytest.fixture
def payload():
    return TaskPayload(caller="TestCaller", delay_seconds=1)


def new_task(payload: TaskPayload, **data) -> Task:
    return Task(payload=payload, state=PendingState(), **data)


def failed_task(payload: TaskPayload, retries_used: int = 0, **data) -> Task:
    task = new_task(payload, **data)
    task.start()
    task.fail()
    for _ in range(retries_used):
        task.retry()
        task.start()
        task.fail()
    return task


def test_start_moves_pending_to_running(payload):
    task = new_task(payload)

    task.start()

    assert task.state.status == TaskStatus.RUNNING


def test_succeed_moves_running_to_succeeded(payload):
    task = new_task(payload)
    task.start()

    task.succeed()

    assert task.state.status == TaskStatus.SUCCEEDED


def test_fail_moves_running_to_failed_without_counting_a_retry(payload):
    task = failed_task(payload)

    assert task.state.status == TaskStatus.FAILED
    assert task.retry_count == 0


def test_failed_task_cannot_start_again(payload):
    task = failed_task(payload)

    with pytest.raises(TaskException) as error:
        task.start()

    assert error.value.failed_task is task
    assert task.state.status == TaskStatus.FAILED


def test_retry_returns_failed_task_to_pending_and_counts_it(payload):
    task = failed_task(payload)

    task.retry()

    assert task.state.status == TaskStatus.PENDING
    assert task.retry_count == 1


def test_retry_limit_defaults_to_three(payload):
    assert new_task(payload).retry_limit == 3


def test_retry_is_refused_when_no_retries_are_left(payload):
    task = failed_task(payload, retries_used=3)

    with pytest.raises(TaskException):
        task.retry()

    assert task.state.status == TaskStatus.FAILED
    assert task.retry_count == 3


def test_dead_letter_ends_failed_task_with_no_retries_left(payload):
    task = failed_task(payload, retries_used=3)

    task.dead_letter()

    assert task.state.status == TaskStatus.DEAD_LETTER


def test_dead_letter_is_refused_while_retries_are_left(payload):
    task = failed_task(payload, retries_used=2)

    with pytest.raises(TaskException):
        task.dead_letter()

    assert task.state.status == TaskStatus.FAILED


def test_retry_limit_of_zero_sends_first_failure_to_dead_letter(payload):
    task = failed_task(payload, retry_limit=0)

    task.dead_letter()

    assert task.state.status == TaskStatus.DEAD_LETTER


@pytest.mark.parametrize("retry_limit", [-1, 11])
def test_retry_limit_outside_bounds_is_rejected(payload, retry_limit):
    with pytest.raises(ValidationError):
        new_task(payload, retry_limit=retry_limit)


@pytest.mark.parametrize("retry_limit", [0, 10])
def test_retry_limit_bounds_are_inclusive(payload, retry_limit):
    assert new_task(payload, retry_limit=retry_limit).retry_limit == retry_limit


def test_retry_limit_cannot_change_after_creation(payload):
    task = new_task(payload)

    with pytest.raises(ValidationError):
        task.retry_limit = 10

    assert task.retry_limit == 3


@pytest.mark.parametrize("action", ["start", "fail", "succeed", "retry", "dead_letter"])
def test_dead_letter_is_final(payload, action):
    task = failed_task(payload, retries_used=3)
    task.dead_letter()

    with pytest.raises(TaskException):
        getattr(task, action)()

    assert task.state.status == TaskStatus.DEAD_LETTER


@pytest.mark.parametrize("action", ["retry", "dead_letter"])
def test_only_a_failed_task_can_be_retried_or_dead_lettered(payload, action):
    pending = new_task(payload)
    running = new_task(payload)
    running.start()

    for task in (pending, running):
        with pytest.raises(TaskException):
            getattr(task, action)()


def test_has_retries_left_compares_count_with_limit(payload):
    assert new_task(payload).has_retries_left()
    assert not new_task(payload, retry_limit=0).has_retries_left()
