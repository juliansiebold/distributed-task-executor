from dataclasses import dataclass
from abc import ABC
from enum import StrEnum
from uuid import UUID
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
    task_id: TaskId
    payload: TaskPayload
    retry_count: int = 0
    lease: Optional[Lease] = None
    _state: "AbstractTaskState"

    def increase_retry(self):
        """Increases retry count. 
            Side effect: If max retries reached, fail task"""
        self.retry_count+1

        # TODO create max retries reached conndition

    def set_lease(self, worker_id: WorkerId) -> None:
        self.lease = Lease(assigned_worker=worker_id)

    def transition_to(self, state: "AbstractTaskState") -> None:
        """Transitions the task to it's next state"""
        self._state = state

class AbstractTaskState(ABC):
    """Abstract interface for Task state handling."""

    def handle_creation(self, task: Task) -> None:
        pass

    def handle_start(self, task: Task, worker_id: WorkerId) -> None:
        pass

    def handle_fail(self, taks: Task) -> None:
        pass

    def handle_success(self, task: Task) -> None:
        pass