from distributed_task_executor.core.models import AbstractTaskState, Task, TaskStatus

class TaskException(Exception):

    failed_task: Task

    def __init__(self, message: str, task: Task):
        super().__init__(message)
        self.failed_task = task

class TaskStateBase(AbstractTaskState):
    """Task Base to handle default task state behavior"""

    def handle_start(self, task: Task) -> None:
        raise TaskException(
            "This state does not allow starting a Task.",
            task=task)

    def handle_fail(self, task: Task) -> None:
        raise TaskException(
            "This state does not allow failing a Task.",
            task=task)

    def handle_success(self, task: Task) -> None:
        raise TaskException(
            "This state does not allow succeeding a Task.",
            task=task)

class PendingState(TaskStateBase):
    """Starts the Task"""

    status = TaskStatus.PENDING

    def handle_start(self, task: Task) -> None:
        """transitions to Running task."""
        task.transition_to(state=RunningState())

class RunningState(TaskStateBase):
    """Handles Success or Failure transition"""

    status = TaskStatus.RUNNING
    def handle_fail(self, task: Task) -> None:
        task.transition_to(state=FailedState())

    def handle_success(self, task: Task) -> None:
        task.transition_to(state=SuccessState())

class FailedState(TaskStateBase):
    """If restarted, increases the retry_count"""

    status = TaskStatus.FAILED

    def handle_start(self, task: Task) -> None:
        task.increase_retry()
        task.transition_to(state=RunningState())

class SuccessState(TaskStateBase):
    """Success State doesn't transition anywhere"""

    status = TaskStatus.SUCCEEDED
    pass