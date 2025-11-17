from dataclasses import dataclass


@dataclass
class TemplateField:
    key: str
    agent_instructions: str


@dataclass
class Template:
    id: str
    title: str
    storage_filename: str
    fields: dict[str, TemplateField]
