from pathlib import Path
import os
from typing import Generator, BinaryIO
from contextlib import contextmanager

from src.core.results.iface import IssueResultFileStorageABC


class FilesystemIssueResultStorageABC(IssueResultFileStorageABC):

    __path: os.PathLike

    def __init__(self, path: os.PathLike):
        self.__path = path

    def __get_filepath(self, issue_id: str) -> os.PathLike:
        return Path(self.__path, f"{issue_id}.docx")

    @contextmanager
    def write_issue_result_file(self, issue_id: str) -> Generator[BinaryIO, None, None]:
        with open(self.__get_filepath(issue_id), "wb") as f:
            yield f
