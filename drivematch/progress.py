from rich.progress import Progress, TaskID

from abc import ABC, abstractmethod


class ProgressReporter(ABC):
    @abstractmethod
    def start(self, description: str, total: int):
        pass

    @abstractmethod
    def advance(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class RichProgressReporter(ProgressReporter):
    progress: Progress
    task_id: TaskID

    def __init__(self, progress: Progress):
        self.progress = progress

    def start(self, description: str, total: int):
        self.task_id = self.progress.add_task(description=description, total=total)
        self.progress.start()

    def advance(self):
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=1)

    def stop(self):
        if self.task_id is not None:
            self.progress.stop()
