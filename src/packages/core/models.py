from dataclasses import dataclass, field
from abc import ABC
from enum import StrEnum
from uuid import UUID, uuid4
from typing import Optional
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

WorkerId = int
TaskId = UUID

@dataclass
class Lease:
    """Locks a task to an assigned worker. Owns TTL definition"""
    assigned_worker: WorkerId
    lease_ttl_seconds: int = 60

    # TODO evaluate if Lease nneeds to be it's own concet. 
    # E.g. it could be handled by the service as worker_id makes more sense to be part of Task

@dataclass
class Task: 
    '''Representation of an arbitrary task to queue into the system for execution'''
    payload: TaskPayload
    _state: "AbstractTaskState"
    task_id: TaskId
    retry_count: int = 0
    lease: Optional[Lease] = None

    def __init__(self, payload: TaskPayload, state: "AbstractTaskState", task_id: Optional[TaskId]=None):
        """init allows for both a newly created task as well a an existing task, read from database"""
        self.payload = payload
        self._state = state
        if task_id is None: 
            self.task_id = uuid4()
        else: 
            self.task_id = task_id

    @property
    def state(self) -> "AbstractTaskState":
        return self._state

    def start(self, worker_id: WorkerId):
        self._state.handle_start(task=self, worker_id=worker_id)

    def succeed(self):
        self._state.handle_success(task=self)

    def fail(self):
        self._state.handle_fail(taks=self)

    def increase_retry(self):
        """Increases retry count. 
            Side effect: If max retries reached, fail task"""
        self.retry_count+1

        # TODO create max retries reached conndition

    def set_lease(self, worker_id: WorkerId) -> None:
        self.lease = Lease(assigned_worker=worker_id)

    def transition_to(self, state: "AbstractTaskState") -> None:
        """Transitions the task to it's next state"""
        self._state = state()

class AbstractTaskState(ABC):

    """Abstract interface for Task state handling."""

    def handle_start(self, task: Task, worker_id: WorkerId) -> None:
        pass

    def handle_fail(self, task: Task) -> None:
        pass

    def handle_success(self, task: Task) -> None:
        pass