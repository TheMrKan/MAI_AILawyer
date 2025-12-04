import os
from typing import BinaryIO, Generator
from contextlib import contextmanager
from pathlib import Path

from src.core.templates.iface import TemplatesFileStorageABC
from src.application.provider import Registerable, Provider, Singleton


class FilesystemTemplatesStorage(TemplatesFileStorageABC, Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        templates_dir = Path(os.getenv("TEMPLATES_DIR") or "")
        if not templates_dir.exists():
            raise Exception("TEMPLATES_DIR env var must be set")
        templates_storage = cls(templates_dir)
        provider.register(TemplatesFileStorageABC, Singleton(templates_storage))

    __path: os.PathLike

    def __init__(self, path: os.PathLike):
        self.__path = path

    @contextmanager
    def open_template_file(self, filename: str) -> Generator[BinaryIO, None, None]:
        with open(os.path.join(self.__path, filename), 'rb') as f:
            yield f

