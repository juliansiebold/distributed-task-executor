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

@dataclass
class Task: 
    '''Representation of an arbitrary task to queue into the system for execution'''
    task_id: TaskId
    task_state: "TaskState"
    payload: TaskPayload

class TaskState(ABC):
    """Abstract interface for Task state handling."""

    def handle_creation(task: Task) -> "TaskState":
        pass

    def handle_start(task: Task, worker_id: WorkerId) -> "TaskState":
        pass

    def handle_fail(taks: Task) -> "TaskState":
        pass

    def handle_success(task: Task) -> "TaskState":
        pass