from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr, Field, ConfigDict, model_validator
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import NoReturn, Self
from uuid import UUID, uuid4

RETRY_LIMIT_DEFAULT = 3
RETRY_LIMIT_MIN = 0
RETRY_LIMIT_MAX = 10
USE_SUPPORTED_TASK_PATHS = "Use Task(...) to create a Task or Task.rehydrate(...) to restore one."

class TaskStatus(StrEnum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'
    DEAD_LETTER = 'Dead Letter'

@dataclass(frozen=True)
class TaskPayload:
    """contract for data type."""
    delay_seconds: int

TaskId = UUID
ClientId = str

class Task(BaseModel):
    '''Representation of an arbitrary task to queue into the system for execution'''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    payload: TaskPayload
    client_id: ClientId = Field(min_length=1)
    task_id: TaskId = Field(default_factory=uuid4, frozen=True)
    retry_count: int = Field(default=0, ge=0, strict=True)
    retry_limit: int = Field(ge=RETRY_LIMIT_MIN, le=RETRY_LIMIT_MAX, frozen=True, strict=True)

    _state: "AbstractTaskState" = PrivateAttr()

    def __init__(
            self,
            *,
            payload: TaskPayload,
            client_id: ClientId,
            retry_limit: int = RETRY_LIMIT_DEFAULT):
        """Creates a new Task, which always starts Pending."""
        # Imported here because task_state.py imports this module.
        from distributed_task_executor.core.task_state import PendingState

        super().__init__(payload=payload, client_id=client_id, retry_limit=retry_limit)
        self._state = PendingState()

    @classmethod
    def rehydrate(
            cls,
            *,
            state: "AbstractTaskState",
            task_id: TaskId,
            payload: TaskPayload,
            client_id: ClientId,
            retry_count: int,
            retry_limit: int) -> Self:
        """Restores a stored Task, applying the same field rules as creating one."""
        if not isinstance(state, AbstractTaskState):
            raise TypeError("A Task can only be rehydrated with a state object.")
        task = cls.__new__(cls)
        # Skips Task.__init__, which only creates new Tasks, but still validates the fields.
        BaseModel.__init__(
            task,
            task_id=task_id,
            payload=payload,
            client_id=client_id,
            retry_count=retry_count,
            retry_limit=retry_limit)
        task._state = state
        return task

    @model_validator(mode="after")
    def _retry_count_within_retry_limit(self) -> Self:
        if self.retry_count > self.retry_limit:
            raise ValueError("The Retry count cannot be above the Retry limit.")
        return self

    @classmethod
    def model_validate(cls, *args, **kwargs) -> NoReturn:
        raise TypeError(USE_SUPPORTED_TASK_PATHS)

    @classmethod
    def model_construct(cls, *args, **kwargs) -> NoReturn:
        raise TypeError(USE_SUPPORTED_TASK_PATHS)

    def model_copy(self, *args, **kwargs) -> NoReturn:
        raise TypeError(USE_SUPPORTED_TASK_PATHS)

    def copy(self, *args, **kwargs) -> NoReturn:
        raise TypeError(USE_SUPPORTED_TASK_PATHS)

    @property
    def state(self) -> "AbstractTaskState":
        return self._state

    def start(self):
        self._state.handle_start(task=self)

    def succeed(self):
        self._state.handle_succeed(task=self)

    def fail(self):
        self._state.handle_fail(task=self)

    def retry(self):
        self._state.handle_retry(task=self)

    def dead_letter(self):
        self._state.handle_dead_letter(task=self)

    def has_retries_left(self) -> bool:
        return self.retry_count < self.retry_limit

    def increase_retry(self):
        """Increases the Retry count. FailedState calls this when it Retries the Task."""
        self.retry_count += 1

    def transition_to(self, state: "AbstractTaskState") -> None:
        """Transitions the task to it's next state"""
        self._state = state

# We define AbstractTaskState in models to keep the core concepts in one central
# place. task_state.py imports this module, so this module can only import
# task_state.py inside a function, as Task.__init__ does.
class AbstractTaskState(ABC):

    """Abstract interface for Task state handling."""
    status: TaskStatus

    @abstractmethod
    def handle_start(self, task: Task) -> None:
        pass

    @abstractmethod
    def handle_fail(self, task: Task) -> None:
        pass

    @abstractmethod
    def handle_succeed(self, task: Task) -> None:
        pass

    @abstractmethod
    def handle_retry(self, task: Task) -> None:
        pass

    @abstractmethod
    def handle_dead_letter(self, task: Task) -> None:
        pass
