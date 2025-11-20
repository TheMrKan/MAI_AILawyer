from abc import ABC, abstractmethod
from functools import wraps
import inspect
import os
from pathlib import Path


class FactoryABC[T](ABC):

    @abstractmethod
    def __call__(self) -> T:
        pass


class Singleton[T](FactoryABC[T]):
    __instance: T | None = None

    def __init__(self, instance: T):
        self.__instance = instance

    def __call__(self, *args, **kwargs) -> T:
        return self.__instance


global_provider: "Provider"


class Provider:
    mapping: dict[type, FactoryABC]

    def __init__(self):
        self.mapping = {Provider: Singleton(self)}

    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        return self.resolve(item)

    def __contains__(self, item: type) -> bool:
        return item in self.mapping.keys()

    def resolve(self, interface: type):
        return self.mapping[interface]()

    def register_singleton[IFACE](self, interface: type[IFACE], instance: IFACE):
        self.mapping[interface] = Singleton(instance)


def inject_global(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        for pname, pvalue in sig.parameters.items():
            if pvalue.annotation not in global_provider:
                continue

            kwargs[pname] = global_provider[pvalue.annotation]
        return await func(*args, **kwargs)

    return wrapper


async def build_async() -> Provider:
    provider = Provider()

    from src.core.llm import LLMABC
    from src.external.cerebras_llm import CerebrasLLM
    provider.register_singleton(LLMABC, CerebrasLLM())

    from src.core.issue_chat_service import IssueChatService
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
    provider.register_singleton(IssueChatService, IssueChatService(checkpointer))

    import chromadb
    chroma_client = await chromadb.AsyncHttpClient(host="chroma", port=8000)

    from src.core.laws import LawDocsRepositoryABC
    from src.external.chroma_law_docs_repo import ChromaLawDocsRepository
    laws_repo = ChromaLawDocsRepository(chroma_client)
    await laws_repo.init_async()
    provider.register_singleton(LawDocsRepositoryABC, laws_repo)

    from src.core.templates.iface import TemplatesRepositoryABC
    from src.external.chroma_templates_repo import ChromaTemplatesRepository
    templates_repo = ChromaTemplatesRepository(chroma_client)
    await templates_repo.init_async()
    provider.register_singleton(TemplatesRepositoryABC, templates_repo)

    from src.core.templates.service import TemplateService
    provider.register_singleton(TemplateService, TemplateService(templates_repo))

    from src.core.templates.iface import TemplatesFileStorageABC
    from src.external.fs_templates_storage import FilesystemTemplatesStorage
    templates_dir = Path(os.getenv("TEMPLATES_DIR") or "")
    if not templates_dir.exists():
        raise Exception("TEMPLATES_DIR env var must be set")
    templates_storage = FilesystemTemplatesStorage(templates_dir)
    provider.register_singleton(TemplatesFileStorageABC, templates_storage)

    from src.core.templates.file_service import TemplateFileService
    provider.register_singleton(TemplateFileService, TemplateFileService(templates_storage))

    from src.core.results.iface import IssueResultFileStorageABC
    from src.external.fs_issue_result_storage import FilesystemIssueResultStorageABC
    results_dir = Path(os.getenv("RESULTS_DIR") or "")
    if not results_dir.exists():
        raise Exception("RESULTS_DIR env var must be set")
    provider.register_singleton(IssueResultFileStorageABC, FilesystemIssueResultStorageABC(results_dir))

    return provider
