from typing import Protocol, Optionnal
from uuid import UUID

from src.packages.core.models import Task, Lease

class TaskQueueProtocol(Protocol):
    """Task queue managing interface"""
    def push_task_id_to_queue(id: UUID) -> None:
        """push a next task to the queue"""
        ...

    def pop_next_task_id() -> UUID:
        """pop the next available taskID, optionally blocking until available"""
        ...

class StateStore(Protocol):

    def write_task(task: Task) -> None:
        """Writes a task into the State Store"""

    def acquire_lease_lock(lease: Lease) -> Lease:
        """"""