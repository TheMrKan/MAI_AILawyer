from docxtpl import DocxTemplate
from typing import BinaryIO

from src.core.templates.iface import TemplatesFileStorageABC
from src.core.templates.types import Template
from src.application.provider import Registerable, Provider, Singleton


class TemplateContentService(Registerable):
    __REG_ORDER__ = 1

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        storage = provider[TemplatesFileStorageABC]
        provider.register(TemplateContentService, Singleton(cls(storage)))

    templates_storage: TemplatesFileStorageABC

    def __init__(self, templates_storage: TemplatesFileStorageABC):
        self.templates_storage = templates_storage

    def __get_docx(self, filename: str) -> DocxTemplate:
        with self.templates_storage.open_template_file(filename) as file:
            tpl = DocxTemplate(file)
            tpl.init_docx()
            return tpl

    def extract_text(self, template: Template) -> str:
        doc = self.__get_docx(template.storage_filename)
        chunks = []

        for p in doc.docx.paragraphs:
            if p.text.strip():
                chunks.append(p.text)

        for table in doc.docx.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        chunks.append(cell.text)

        return "\n".join(chunks)

    def fill_with_values(self, template: Template, values: dict[str, str], output: BinaryIO):
        doc = self.__get_docx(template.storage_filename)
        doc.render(values)
        doc.save(output)
