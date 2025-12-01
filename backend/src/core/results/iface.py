from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import BinaryIO, Generator


class IssueResultFileStorageABC(ABC):

    @abstractmethod
    @contextmanager
    def write_issue_result_file(self, issue_id: int) -> Generator[BinaryIO, None, None]:
        pass

    @abstractmethod
    @contextmanager
    def read_issue_result_file(self, issue_id: int) -> Generator[BinaryIO, None, None]:
        pass
