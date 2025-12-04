from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
import logging

from src.core.laws.iface import LawDocsRepositoryABC
from src.application.provider import Provider
from src.core.laws.types import LawFragment as DtoLawFragment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/laws", tags=["laws"])


class LawFragmentSchema(BaseModel):
    fragment_id: str
    document_id: str
    content: str

    @classmethod
    def from_dto(cls, dto: DtoLawFragment) -> "LawFragmentSchema":
        return cls(fragment_id=dto.fragment_id, document_id=dto.document_id, content=dto.content)


class AddOrUpdateLawFragmentSchema(BaseModel):
    fragment_id: str
    document_id: str
    content: str

    def to_dto(self) -> DtoLawFragment:
        return DtoLawFragment(fragment_id=self.fragment_id, document_id=self.document_id, content=self.content)


@router.get("/", response_model=list[LawFragmentSchema])
async def list_fragments(
    provider: Provider = Depends(Provider)
):
    try:
        repo: LawDocsRepositoryABC = provider[LawDocsRepositoryABC]
        fragments = await repo.list_fragments_async()
        return [LawFragmentSchema.from_dto(frag) for frag in fragments]
    except Exception as e:
        logger.exception("Error listing law fragments", exc_info=e)
        raise HTTPException(status_code=500, detail="Не удалось получить список фрагментов")


@router.get("/search", response_model=list[LawFragmentSchema])
async def search_fragments(
    query: str,
    provider: Provider = Depends(Provider)
):
    try:
        repo: LawDocsRepositoryABC = provider[LawDocsRepositoryABC]
        fragments = await repo.find_fragments_async(query=query)
        return [LawFragmentSchema.from_dto(frag) for frag in fragments]
    except Exception as e:
        logger.exception("Error searching law fragments", exc_info=e)
        raise HTTPException(status_code=500, detail="Ошибка при поиске фрагментов")


@router.post("/", response_model=LawFragmentSchema)
async def add_or_update_fragment(
    fragment: AddOrUpdateLawFragmentSchema,
    provider: Provider = Depends(Provider)
):
    try:
        repo: LawDocsRepositoryABC = provider[LawDocsRepositoryABC]
        await repo.add_of_update_fragment_async(fragment.to_dto())
        return fragment
    except Exception as e:
        logger.exception("Error adding/updating law fragment", exc_info=e)
        raise HTTPException(status_code=500, detail="Не удалось добавить или обновить фрагмент")


@router.delete("/{fragment_id}")
async def delete_fragment(
    fragment_id: str,
    response: Response,
    provider: Provider = Depends(Provider),
):
    try:
        repo: LawDocsRepositoryABC = provider[LawDocsRepositoryABC]
        await repo.delete_fragment_async(fragment_id)
        response.status_code = 204
    except Exception as e:
        logger.exception("Error deleting law fragment", exc_info=e)
        raise HTTPException(status_code=500, detail="Не удалось удалить фрагмент")
