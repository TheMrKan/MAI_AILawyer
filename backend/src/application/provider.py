from abc import ABC, abstractmethod
from functools import wraps
import inspect
import os
from pathlib import Path
from typing import Any, Self, Callable


class ServiceResolverABC(ABC):

    @abstractmethod
    def resolve[IFACE](self, interface: type[IFACE], resolver: Self | None = None) -> IFACE:
        pass

    @abstractmethod
    def __contains__(self, item: type) -> bool:
        pass

    @abstractmethod
    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        pass


global_provider: "Provider"


def _get_injectables(func: Callable, source: ServiceResolverABC) -> dict[str, Any]:
    values = {}
    sig = inspect.signature(func)
    for pname, pvalue in sig.parameters.items():
        if pvalue.annotation not in source:
            continue

        values[pname] = source.resolve(pvalue.annotation)
    return values


def inject_global(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        injectables = _get_injectables(func, global_provider)
        kwargs.update(injectables)
        return await func(*args, **kwargs)

    return wrapper


class FactoryABC[T](ABC):

    @abstractmethod
    def __call__(self, resolver: ServiceResolverABC) -> T:
        pass


class Singleton[T](FactoryABC[T]):
    __instance: T | None = None

    def __init__(self, instance: T):
        self.__instance = instance

    def __call__(self, resolver: ServiceResolverABC) -> T:
        return self.__instance


class Transient[T](FactoryABC[T]):
    __cls: type[T]

    def __init__(self, cls: type[T]):
        self.__cls = cls

    def __call__(self, resolver: ServiceResolverABC) -> T:
        injectables = _get_injectables(self.__cls, resolver)
        return self.__cls(**injectables)


class Provider(ServiceResolverABC):
    mapping: dict[type, FactoryABC]

    def __init__(self):
        self.mapping = {Provider: Singleton(self)}

    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        return self.resolve(item)

    def __contains__(self, item: type) -> bool:
        return item in self.mapping.keys()

    def resolve[IFACE](self, interface: type[IFACE], resolver: ServiceResolverABC | None = None) -> IFACE:
        return self.mapping[interface](resolver)

    def register[IFACE](self, iface: type[IFACE], factory: FactoryABC[IFACE]):
        self.mapping[iface] = factory


class Scope(ServiceResolverABC):

    __scope_instances: dict[type, Any]
    parent: ServiceResolverABC | None

    def __init__(self, parent: ServiceResolverABC | None = None, *instances: Any):
        self.parent = parent
        self.__scope_instances = {type(i): i for i in instances}

    def resolve[IFACE](self, interface: type[IFACE], resolver: ServiceResolverABC | None = None) -> IFACE:
        value = self.__scope_instances.get(interface, None)
        if value:
            return value

        if self.parent:
            return self.parent.resolve(interface, resolver or self)
        raise KeyError

    def __contains__(self, item: type) -> bool:
        return item in self.__scope_instances.keys() or (self.parent and item in self.parent)

    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        return self.resolve(item)

    def set_scoped_value[IFACE](self, value: IFACE, iface: type[IFACE] | None = None):
        self.__scope_instances[iface or type(value)] = value


async def build_async() -> Provider:
    provider = Provider()

    from src.core.llm.iface import LLMABC
    from src.external.cerebras_llm import CerebrasLLM
    provider.register(LLMABC, Singleton(CerebrasLLM()))

    from src.core.chats.service import IssueChatService
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
    provider.register(IssueChatService, Singleton(IssueChatService(checkpointer)))

    import chromadb
    chroma_client = await chromadb.AsyncHttpClient(host="chroma", port=8000)

    from src.core.laws.iface import LawDocsRepositoryABC
    from src.external.chroma_law_docs_repo import ChromaLawDocsRepository
    laws_repo = ChromaLawDocsRepository(chroma_client)
    await laws_repo.init_async()
    provider.register(LawDocsRepositoryABC, Singleton(laws_repo))

    from src.core.templates.iface import TemplatesRepositoryABC
    from src.external.chroma_templates_repo import ChromaTemplatesRepository
    templates_repo = ChromaTemplatesRepository(chroma_client)
    await templates_repo.init_async()
    provider.register(TemplatesRepositoryABC, Singleton(templates_repo))

    from src.core.templates.manager import TemplateManager
    provider.register(TemplateManager, Singleton(TemplateManager(templates_repo)))

    from src.core.templates.iface import TemplatesFileStorageABC
    from src.external.fs_templates_storage import FilesystemTemplatesStorage
    templates_dir = Path(os.getenv("TEMPLATES_DIR") or "")
    if not templates_dir.exists():
        raise Exception("TEMPLATES_DIR env var must be set")
    templates_storage = FilesystemTemplatesStorage(templates_dir)
    provider.register(TemplatesFileStorageABC, Singleton(templates_storage))

    from src.core.templates.content_service import TemplateContentService
    provider.register(TemplateContentService, Singleton(TemplateContentService(templates_storage)))

    from src.core.results.iface import IssueResultFileStorageABC
    from src.external.fs_issue_result_storage import FilesystemIssueResultStorageABC
    results_dir = Path(os.getenv("RESULTS_DIR") or "")
    if not results_dir.exists():
        raise Exception("RESULTS_DIR env var must be set")
    provider.register(IssueResultFileStorageABC, Singleton(FilesystemIssueResultStorageABC(results_dir)))

    from src.core.users.iface import OAuthProviderABC
    from src.external.google_oauth import GoogleOAuth
    google_oauth = GoogleOAuth()
    provider.register(OAuthProviderABC, Singleton(google_oauth))
    provider.register(GoogleOAuth, Singleton(google_oauth))

    from src.core.users.iface import AuthServiceABC
    from src.core.users.auth_service import AuthService
    provider.register(AuthServiceABC, Singleton(AuthService()))

    from src.core.users.iface import UserRepositoryABC
    from src.database.user import UserRepository
    provider.register(UserRepositoryABC, Transient(UserRepository))

    from src.core.issue_service import IssueService
    provider.register(IssueService, Transient(IssueService))

    return provider
