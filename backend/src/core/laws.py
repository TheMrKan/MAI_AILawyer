from abc import ABC, abstractmethod

from src.dto.laws import LawFragment


class AbstractLawDocsRepository(ABC):

    @abstractmethod
    async def find_fragments_async(self, query: str) -> list[LawFragment]:
        pass


class TempLawDocsRepository(AbstractLawDocsRepository):

    __FRAGMENTS = [
        LawFragment(1,
        """
        Статья 114. Право на отпуск
        Каждому работнику предоставляется ежегодный оплачиваемый отпуск с сохранением места работы и среднего заработка.
        """),
        LawFragment(2,
        """
        Статья 115. Продолжительность отпуска
        Минимальная продолжительность — 28 календарных дней. Для некоторых категорий работников (например, педагогов или госслужащих) отпуск может быть длиннее.
        """),
        LawFragment(3,
        """
        Статья 123. График отпусков
        График утверждается работодателем не позднее чем за 2 недели до нового года, и работник должен быть уведомлён о начале отпуска не позднее чем за 2 недели.
        """),
        LawFragment(4,
        """
        Статья 125. Разделение отпуска
        Отпуск можно разделить на части, но одна из них должна быть не меньше 14 календарных дней.
        """),
        LawFragment(5,
        """
        Статья 126. Денежная компенсация
        Неиспользованные дни отпуска можно заменить деньгами, но только за часть, превышающую 28 дней (основной отпуск деньгами не заменяется, кроме увольнения).
        """)
    ]

    async def find_fragments_async(self, query: str) -> list[LawFragment]:
        return self.__FRAGMENTS.copy()