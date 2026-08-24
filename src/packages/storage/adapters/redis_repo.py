from typing import Protocol, Optionnal
from uuid import uuid4

class TaskQueueProtocol(Protocol):
    """Task queue managing interface"""
    def push_task_id_to_queue(id: uuid4) -> None:
        """push a next task to the queue"""
        ...

    def pop_next_task_id() -> uuid4:
        """pop the next available taskID, optionally blocking until available"""
        ...

class RedisTaskRepository(TaskQueueProtocol):
    """Redis tasks queue mannager implementation"""
    pass