from .models import AbstractTaskState, Task, WorkerId

class TaskException(Exception):
    pass

class TaskStateBase(AbstractTaskState):
    """Task Base to handle default task state behavior"""
        
    def handle_creation(self, task: Task) -> None:
        raise TaskException("This state does not allow Task creation ")

    def handle_start(self, task: Task, worker_id: WorkerId) -> None:
        raise TaskException("This state does not allow starting a Task ")

    def handle_fail(self, task: Task) -> None:
        raise TaskException("This state does not allow failing a Task")

    def handle_success(self, task: Task) -> None:
        raise TaskException("This state does not allow succeeding a Task")

class PendingTask(TaskStateBase):
    """Starts the Task if called"""
    def handle_start(self, task: Task, worker_id: WorkerId) -> None:
        task.set_lease(worker_id=worker_id)
        task.transition_to(state="RunningState")

class RunningTask(TaskStateBase):
    """Handles Success or Failure transition"""
    def handle_fail(self, task: Task) -> None:
        task.transition_to(state="FailedState")

    def handle_success(self, task: Task) -> None:
        task.transition_to(state="SuccessState")

class FailedState(TaskStateBase):
    """If restarted, increases the retry_count"""
    def handle_start(self, task: Task, worker_id: WorkerId) -> None:
        task.increase_retry()
        task.set_lease(worker_id=worker_id)
        task.transition_to(state="RunningState")

class SuccessState(TaskStateBase):
    """Success State doesn't transition anywhere"""
    pass