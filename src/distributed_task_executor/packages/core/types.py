from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4

class TaskStatus(StrEnum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    FAILED = 'Failed'


class Task(dataclass): 
    id: uuid4
    task_status: TaskStatus