from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from models import Interaction
from schemas import InteractionCreate, InteractionResponse, InteractionUpdate

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionResponse)
async def create_interaction(payload: InteractionCreate, db: AsyncSession = Depends(get_db)):
    interaction = Interaction(**payload.model_dump())
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    return interaction


@router.get("", response_model=list[InteractionResponse])
async def list_interactions(hcp_id: str | None = Query(default=None), db: AsyncSession = Depends(get_db)):
    query = select(Interaction).order_by(Interaction.created_at.desc())
    if hcp_id:
        query = query.where(Interaction.hcp_id == hcp_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(interaction_id: str, db: AsyncSession = Depends(get_db)):
    interaction = await db.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(interaction_id: str, payload: InteractionUpdate, db: AsyncSession = Depends(get_db)):
    interaction = await db.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(interaction, key, value)
    await db.commit()
    await db.refresh(interaction)
    return interaction
