from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.submission import Contributor
from pydantic import BaseModel, EmailStr




router = APIRouter(prefix="/api/contributors", tags=["contributors"])

class ContributorCreate(BaseModel):
    name: str
    email: EmailStr
    county: str
    language: str


@router.post("/")
async def create_contributor(data: ContributorCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Contributor).where(Contributor.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code = 409, detail = "Email already registered")

    contributor = contributor(**data.model_dump())
    db.add(contributor)
    await db.commit()
    await db.refresh(contributor)
    return contributor


@router.get("/{contributor_id}")
async def get_contributor(contributor_id: str, db: AsyncSession = Depends(get_db)):
    contributor = await db.get(Contributor, contributor_id)

    if not contributor:
        raise HTTPException(status_code = 404, detail = "Contributor not found")
    return contributor

