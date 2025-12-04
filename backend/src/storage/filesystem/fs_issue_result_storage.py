from pathlib import Path
import os
from typing import Generator, BinaryIO
from contextlib import contextmanager

from src.core.results.iface import IssueResultFileStorageABC
from src.application.provider import Registerable, Provider, Singleton


class FilesystemIssueResultStorageABC(IssueResultFileStorageABC, Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        results_dir = Path(os.getenv("RESULTS_DIR") or "")
        if not results_dir.exists():
            raise Exception("RESULTS_DIR env var must be set")
        provider.register(IssueResultFileStorageABC, Singleton(cls(results_dir)))

    __path: os.PathLike

    def __init__(self, path: os.PathLike):
        self.__path = path

    def __get_filepath(self, issue_id: int) -> os.PathLike:
        return Path(self.__path, f"{issue_id}.docx")

    @contextmanager
    def write_issue_result_file(self, issue_id: int) -> Generator[BinaryIO, None, None]:
        with open(self.__get_filepath(issue_id), "wb") as f:
            yield f

    @contextmanager
    def read_issue_result_file(self, issue_id: int) -> Generator[BinaryIO, None, None]:
        filepath = self.__get_filepath(issue_id)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File for issue {issue_id} not found")
        with open(filepath, "rb") as f:
            yield f