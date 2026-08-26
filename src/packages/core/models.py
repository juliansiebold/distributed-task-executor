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

@dataclass()
class Task(): 
    '''Representation of an arbitrary task to queue into the system for execution'''
    id: UUID
    task_status: TaskStatus = TaskStatus.PENDING
    payload: TaskPayload

WorkerId = int

class Lease:
    """Locks a task to an assigned worker"""
    lease_ttl_seconds: int
    assigned_worker: WorkerId
    Task: Task

# TODO Needs state managemennt for Task