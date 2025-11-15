from dataclasses import dataclass


@dataclass
class Template:
    id: str
    title: str
    storage_filename: str


@dataclass
class FreeTemplate(Template):
    pass


@dataclass
class StrictTemplateField:
    key: str
    agent_instructions: str


@dataclass
class StrictTemplate(Template):
    fields: dict[str, StrictTemplateField]
