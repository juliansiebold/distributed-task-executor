from dataclasses import dataclass
from abc import ABC
from enum import StrEnum
from uuid import UUID

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

class Lease:
    """Locks a task to an assigned worker. Owns TTL definition"""
    lease_ttl_seconds: int
    assigned_worker: WorkerId
    task_id = TaskId

    # TODO evaluate if Lease nneeds to be it's own concet. 
    # E.g. it could be handled by the service as worker_id makes more sense to be part of Task

@dataclass
class Task: 
    '''Representation of an arbitrary task to queue into the system for execution'''
    task_id: TaskId
    payload: TaskPayload
    _state: "AbstractTaskState"

    def transition_to(self, state: "AbstractTaskState") -> None:
        """Transitions the task to it's next state"""
        self._state = state

class AbstractTaskState(ABC):
    """Abstract interface for Task state handling."""

    def handle_creation(task: Task) -> None:
        pass

    def handle_start(task: Task, worker_id: WorkerId) -> None:
        pass

    def handle_fail(taks: Task) -> None:
        pass

    def handle_success(task: Task) -> None:
        pass