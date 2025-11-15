import os
from typing import BinaryIO, Generator
from contextlib import contextmanager

from src.core.templates.iface import TemplatesFileStorageABC


class FilesystemTemplatesStorage(TemplatesFileStorageABC):

    __path: os.PathLike

    def __init__(self, path: os.PathLike):
        self.__path = path

    @contextmanager
    def open_template_file(self, filename: str) -> Generator[BinaryIO, None, None]:
        with open(os.path.join(self.__path, filename), 'rb') as f:
            yield f

