from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core.llm import AbstractLLM


class Container:
    LLM_instance: "AbstractLLM"


    @classmethod
    def build(cls):
        from src.core.llm import CerebrasLLM
        cls.LLM_instance = CerebrasLLM()