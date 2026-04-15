from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HCPCreate(BaseModel):
    full_name: str
    specialty: str | None = None
    institution: str | None = None
    email: str | None = None
    phone: str | None = None
    territory: str | None = None


class HCPResponse(HCPCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
