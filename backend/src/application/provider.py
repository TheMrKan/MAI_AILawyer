from abc import ABC, abstractmethod
from functools import wraps
import inspect


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

    from core.llm import LLMABC
    from external.cerebras_llm import CerebrasLLM
    provider.register_singleton(LLMABC, CerebrasLLM())

    from core.graph_controller import GraphController
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
    provider.register_singleton(GraphController, GraphController(checkpointer))

    from core.laws import LawDocsRepositoryABC
    from external.chroma_law_docs_repo import ChromaLawDocsRepository
    chroma_repo = ChromaLawDocsRepository("chroma", 8000)
    await chroma_repo.init_async()
    provider.register_singleton(LawDocsRepositoryABC, chroma_repo)

    return provider
