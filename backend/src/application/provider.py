from abc import ABC, abstractmethod
from typing import TypeVar


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


class Provider:
    mapping: dict[type, FactoryABC]

    def __init__(self):
        self.mapping = {Provider: Singleton(self)}

    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        return self.resolve(item)

    def resolve(self, interface: type):
        return self.mapping[interface]()

    def register_singleton[IFACE](self, interface: type[IFACE], instance: IFACE):
        self.mapping[interface] = Singleton(instance)


def build() -> Provider:
    provider = Provider()

    from src.core.llm import LLMABC, CerebrasLLM
    provider.register_singleton(LLMABC, CerebrasLLM())

    from src.core.graph_controller import GraphController
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
    provider.register_singleton(GraphController, GraphController(checkpointer))

    from src.core.laws import LawDocsRepositoryABC, TempLawDocsRepository
    provider.register_singleton(LawDocsRepositoryABC, TempLawDocsRepository())

    return provider
