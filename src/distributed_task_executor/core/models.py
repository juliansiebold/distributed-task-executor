from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr, Field, ConfigDict
from abc import ABC, abstractmethod
from enum import StrEnum
from uuid import UUID, uuid4

RETRY_LIMIT_DEFAULT = 3
RETRY_LIMIT_MIN = 0
RETRY_LIMIT_MAX = 10

class TaskStatus(StrEnum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'
    DEAD_LETTER = 'Dead Letter'

@dataclass(frozen=True)
class TaskPayload:
    """contract for data type."""
    caller: str
    delay_seconds: int

TaskId = UUID

class Task(BaseModel): 
    '''Representation of an arbitrary task to queue into the system for execution'''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    payload: TaskPayload
    task_id: TaskId = Field(default_factory=uuid4)
    retry_count: int = Field(default=0, ge=0, strict=True)
    retry_limit: int = Field(
        default=RETRY_LIMIT_DEFAULT, ge=RETRY_LIMIT_MIN, le=RETRY_LIMIT_MAX, frozen=True,
        strict=True)

    _state: "AbstractTaskState" = PrivateAttr()

    def __init__(self, state: "AbstractTaskState", **data):
        super().__init__(**data)
        self._state = state

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
# place. We avoid circular dependencies to task_state.py. 
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
