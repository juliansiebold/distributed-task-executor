from dataclasses import dataclass
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
    lease_ttl_seconds: intw
    assigned_worker: WorkerId
    task_id = TaskId

@dataclass
class Task: 
    '''Representation of an arbitrary task to queue into the system for execution'''
    task_id = TaskId
    task_status: TaskStatus = TaskStatus.PENDING
    payload: TaskPayload

    # TODO Needs state managemennt for Task
