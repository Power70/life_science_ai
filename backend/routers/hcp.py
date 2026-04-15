from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from models import HCP
from schemas import HCPCreate, HCPResponse

router = APIRouter(prefix="/hcp", tags=["hcp"])


@router.get("/search", response_model=list[HCPResponse])
async def search_hcp(q: str = Query(default=""), db: AsyncSession = Depends(get_db)):
    query = select(HCP).where(HCP.full_name.ilike(f"%{q}%")).order_by(HCP.full_name.asc()).limit(20)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=HCPResponse)
async def create_hcp(payload: HCPCreate, db: AsyncSession = Depends(get_db)):
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    await db.commit()
    await db.refresh(hcp)
    return hcp


@router.get("/{hcp_id}", response_model=HCPResponse)
async def get_hcp(hcp_id: str, db: AsyncSession = Depends(get_db)):
    hcp = await db.get(HCP, hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp
