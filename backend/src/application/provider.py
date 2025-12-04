"""
Простой самописный Dependency Injection, чтобы не привязывать core к Depends от FastAPI.
Не буду скрывать - ориентировался на DI из C#, т. к. он мне привычнее.
"""

from abc import ABC, abstractmethod
from functools import wraps
import inspect
import os
from pathlib import Path
from typing import Any, Self, Callable, overload
import pkgutil
import importlib
import logging


_logger = logging.getLogger(__name__)
global_provider: "Provider"
"""
Глобальный провайдер, использующийся в inject_global
для функций в которые нельзя пробросить провайдер из эндпоинтов.
"""


class ServiceResolverABC(ABC):
    """
    Интерфейс источника сервисов.
    """

    @abstractmethod
    def resolve[IFACE](self, interface: type[IFACE], resolver: Self | None = None) -> IFACE:
        """
        :param interface: Класс-интерфейс, для которого нужно вернуть реализацию.
        :param resolver: Источник сервисов, который будет использован для создания объекта в фабрике.
            Нужен для передачи родительских Scope.
        :return: Объект, реализующий заданный интерфейс.
        """
        pass

    @abstractmethod
    def __contains__(self, item: type) -> bool:
        """
        Проверяет, что источник может вернуть реализацию для данного интерфейса.
        """
        pass

    @abstractmethod
    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        """
        Шорткат для resolve
        """
        pass


def _get_injectables(func: Callable, source: ServiceResolverABC) -> dict[str, Any]:
    """
    Получает аргументы функции, которые могут быть взяты из источника сервисов.
    :param func: Функция, под сигнатуру которой будут получаться объекты.
    :param source: Источник сервисов
    :return: Словарь {"arg_name": obj}, где obj реализует интерфейс, указанный в аннотации arg_name
    """
    values = {}
    sig = inspect.signature(func)
    for pname, pvalue in sig.parameters.items():
        if pvalue.annotation not in source:
            continue

        values[pname] = source.resolve(pvalue.annotation)
    return values


def inject_global(func: Callable):
    """
    Декоратор для автоматического инжекта всех возможных аргументов функции из global_provider при каждом вызове.
    Используется в нодах графа, т. к. туда сложно передать провайдер из эндпоинтов.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        injectables = _get_injectables(func, global_provider)
        kwargs.update(injectables)
        return await func(*args, **kwargs)

    return wrapper


class FactoryABC[T](ABC):
    """
    Интерфейс фабрики. Провайдер хранит не конкретные классы реализации или объекты, а фабрики.
    Через фабрику реализуется lifetime Transient и Singleton.
    Не совсем корректно, но DI развивался постепенно и полностью переписывать на середине было нецелесообразно.
    """

    @abstractmethod
    def __call__(self, resolver: ServiceResolverABC) -> T:
        pass


class Singleton[T](FactoryABC[T]):
    """
    Фабрика, реализующая singleton lifetime.
    Объект реализации создается в момент сборки контейнера и используется везде.
    """
    __instance: T | None = None

    def __init__(self, instance: T):
        self.__instance = instance

    def __call__(self, resolver: ServiceResolverABC) -> T:
        return self.__instance


class Transient[T](FactoryABC[T]):
    """
    Фабрика, реализующая transient lifetime.
    Создает новый объект реализации при каждом вызове через конструктор указанного класса.
    Инжектит зависимости в конструктор через resolver (тот самый параметр resolver в ServiceResolverABC.resolve)
    """
    __cls: type[T]

    def __init__(self, cls: type[T]):
        self.__cls = cls

    def __call__(self, resolver: ServiceResolverABC) -> T:
        injectables = _get_injectables(self.__cls, resolver)
        return self.__cls(**injectables)


class Provider(ServiceResolverABC):
    """
    Основная коллекция сервисов. Почти аналог IServiceProvider из C#.
    """
    mapping: dict[type, FactoryABC]
    """
    Класс интерфейса: фабрика
    """

    def __init__(self):
        # добавляет себя, чтобы можно было получать provider внутри сервисов
        self.mapping = {Provider: Singleton(self)}

    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        """
        Шорткат для resolve
        """
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


class Registerable(ABC):

    __REG_ORDER__ = 0

    @classmethod
    @abstractmethod
    async def on_build_provider(cls, provider: Provider):
        pass


def __find_registerables() -> list[tuple[int, type[Registerable]]]:
    result = []
    unique = set()

    import src
    package_path = Path(src.__file__).parent

    for module_info in pkgutil.walk_packages([str(package_path)], "src."):
        module = importlib.import_module(module_info.name)

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj in unique:
                continue

            if issubclass(obj, Registerable) and obj is not Registerable:
                if hasattr(obj, "__REG_ORDER__"):
                    priority = getattr(obj, "__REG_ORDER__")
                else:
                    priority = 0
                unique.add(obj)
                result.append((priority, obj))

    result.sort(key=lambda i: i[0])
    return result


async def build_async() -> Provider:
    provider = Provider()

    registerables = __find_registerables()
    _logger.info("Found %s registerable classes...", len(registerables))

    for priority, cls in registerables:
        try:
            await cls.on_build_provider(provider)
        except Exception as e:
            _logger.error("Failed to register class %s in provider", cls, exc_info=e)

    return provider
