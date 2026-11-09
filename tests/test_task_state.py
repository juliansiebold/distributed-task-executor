from uuid import uuid4

import pytest
from pydantic import ValidationError

from distributed_task_executor.core.models import Task, TaskPayload, TaskStatus
from distributed_task_executor.core.task_state import (
    DeadLetterState,
    FailedState,
    PendingState,
    RunningState,
    SucceededState,
)


@pytest.fixture
def payload():
    return TaskPayload(delay_seconds=1)


def new_task(payload: TaskPayload, **data) -> Task:
    return Task(payload=payload, client_id="test-client", **data)


def test_new_task_starts_pending_with_no_retries_used(payload):
    task = new_task(payload)

    assert task.state.status == TaskStatus.PENDING
    assert task.retry_count == 0


def test_new_task_records_its_client(payload):
    assert new_task(payload).client_id == "test-client"


def test_new_tasks_get_different_task_ids(payload):
    assert new_task(payload).task_id != new_task(payload).task_id


@pytest.mark.parametrize(
    "field",
    ["state", "task_id", "retry_count"])
def test_new_task_cannot_set_fields_only_rehydrate_restores(payload, field):
    values = {"state": PendingState(), "task_id": uuid4(), "retry_count": 0}

    with pytest.raises(TypeError):
        new_task(payload, **{field: values[field]})


def test_client_id_must_not_be_empty(payload):
    with pytest.raises(ValidationError):
        Task(payload=payload, client_id="")


def rehydrated_task(payload: TaskPayload, **overrides) -> Task:
    stored = {
        "state": FailedState(),
        "task_id": uuid4(),
        "payload": payload,
        "client_id": "test-client",
        "retry_count": 1,
        "retry_limit": 3,
    }
    return Task.rehydrate(**(stored | overrides))


@pytest.mark.parametrize(
    "state, status",
    [
        (PendingState(), TaskStatus.PENDING),
        (RunningState(), TaskStatus.RUNNING),
        (FailedState(), TaskStatus.FAILED),
        (SucceededState(), TaskStatus.SUCCEEDED),
        (DeadLetterState(), TaskStatus.DEAD_LETTER),
    ],
    ids=lambda value: value if isinstance(value, TaskStatus) else "")
def test_rehydrate_restores_every_state(payload, state, status):
    assert rehydrated_task(payload, state=state).state.status == status


def test_rehydrate_restores_every_field(payload):
    task_id = uuid4()

    task = rehydrated_task(
        payload, task_id=task_id, client_id="stored-client", retry_count=2, retry_limit=5)

    assert task.task_id == task_id
    assert task.payload == payload
    assert task.client_id == "stored-client"
    assert task.retry_count == 2
    assert task.retry_limit == 5


def test_rehydrated_task_continues_its_lifecycle(payload):
    task = rehydrated_task(payload, state=FailedState(), retry_count=1, retry_limit=3)

    task.retry()

    assert task.state.status == TaskStatus.PENDING
    assert task.retry_count == 2


def test_rehydrate_allows_retry_count_equal_to_retry_limit(payload):
    task = rehydrated_task(payload, retry_count=3, retry_limit=3)

    assert not task.has_retries_left()


def test_rehydrate_rejects_retry_count_above_retry_limit(payload):
    with pytest.raises(ValidationError):
        rehydrated_task(payload, retry_count=4, retry_limit=3)


@pytest.mark.parametrize("retry_count", [-1, True, "1"])
def test_rehydrate_requires_retry_count_to_be_a_non_negative_int(payload, retry_count):
    with pytest.raises(ValidationError):
        rehydrated_task(payload, retry_count=retry_count)


@pytest.mark.parametrize("retry_limit", [-1, 11, True])
def test_rehydrate_applies_the_retry_limit_rules(payload, retry_limit):
    with pytest.raises(ValidationError):
        rehydrated_task(payload, retry_count=0, retry_limit=retry_limit)


@pytest.mark.parametrize("state", [None, "Failed", TaskStatus.FAILED, FailedState])
def test_rehydrate_requires_a_state_object(payload, state):
    with pytest.raises(TypeError):
        rehydrated_task(payload, state=state)


def test_rehydrate_rejects_an_empty_client_id(payload):
    with pytest.raises(ValidationError):
        rehydrated_task(payload, client_id="")


def test_model_validate_raises_and_points_to_the_supported_paths(payload):
    stored = {"payload": payload, "client_id": "test-client", "retry_count": 99}

    with pytest.raises(TypeError, match="rehydrate"):
        Task.model_validate(stored)


def test_model_copy_raises_and_points_to_the_supported_paths(payload):
    task = new_task(payload)

    with pytest.raises(TypeError, match="rehydrate"):
        task.model_copy(update={"retry_count": 99})

    assert task.retry_count == 0


def test_model_construct_raises_and_points_to_the_supported_paths(payload):
    with pytest.raises(TypeError, match="rehydrate"):
        Task.model_construct(payload=payload, client_id="", retry_count=99)


def test_deprecated_copy_raises_and_points_to_the_supported_paths(payload):
    task = new_task(payload)

    with pytest.raises(TypeError, match="rehydrate"):
        task.copy(update={"retry_count": 99})

    assert task.retry_count == 0


def test_task_id_cannot_change_after_creation(payload):
    task = new_task(payload)
    task_id = task.task_id

    with pytest.raises(ValidationError):
        task.task_id = uuid4()

    assert task.task_id == task_id


def test_task_still_supports_repr_and_equality(payload):
    task = new_task(payload)

    assert "test-client" in repr(task)
    assert task == task
    assert task != new_task(payload)


def test_retry_limit_defaults_to_three(payload):
    assert new_task(payload).retry_limit == 3


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


def test_has_retries_left_compares_count_with_limit(payload):
    assert new_task(payload).has_retries_left()
    assert not new_task(payload, retry_limit=0).has_retries_left()


@pytest.mark.parametrize("retry_limit", [True, "3", 2.0])
def test_retry_limit_must_be_an_int(payload, retry_limit):
    with pytest.raises(ValidationError):
        new_task(payload, retry_limit=retry_limit)
