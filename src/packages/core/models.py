from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr, Field, ConfigDict
from abc import ABC, abstractmethod
from enum import StrEnum
from uuid import UUID, uuid4

class TaskStatus(StrEnum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'

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
    retry_count: int = 0

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
        self._state.handle_success(task=self)

    def fail(self):
        self._state.handle_fail(task=self)

    def increase_retry(self):
        """Increases retry count. 
            Side effect: If max retries reached, fail task"""
        self.retry_count += 1

        # TODO create max retries reached condition

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
    def handle_success(self, task: Task) -> None:
        pass