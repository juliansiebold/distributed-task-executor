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

    def handle_succeed(self, task: Task) -> None:
        raise TaskException(
            "This state does not allow succeeding a Task.",
            task=task)

    def handle_retry(self, task: Task) -> None:
        raise TaskException(
            "This state does not allow retrying a Task.",
            task=task)

    def handle_dead_letter(self, task: Task) -> None:
        raise TaskException(
            "This state does not allow sending a Task to Dead Letter.",
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

    def handle_succeed(self, task: Task) -> None:
        task.transition_to(state=SucceededState())

class FailedState(TaskStateBase):
    """Waits for the Orchestrator Watchdog to Retry the Task or send it to Dead Letter"""

    status = TaskStatus.FAILED

    def handle_retry(self, task: Task) -> None:
        if not task.has_retries_left():
            raise TaskException("This Task has no Retries left.", task=task)
        task.increase_retry()
        task.transition_to(state=PendingState())

    def handle_dead_letter(self, task: Task) -> None:
        if task.has_retries_left():
            raise TaskException("This Task still has Retries left.", task=task)
        task.transition_to(state=DeadLetterState())

class SucceededState(TaskStateBase):
    """Succeeded is final, so it allows no transitions"""

    status = TaskStatus.SUCCEEDED

class DeadLetterState(TaskStateBase):
    """Dead Letter is final, so it allows no transitions"""

    status = TaskStatus.DEAD_LETTER
