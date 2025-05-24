from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Accelerator(BaseModel):
    university: str
    description: str | None = None
    is_active: bool = True

class AcceleratorCreate(Accelerator):
    pass

class AcceleratorUpdate(BaseModel):
    university: str | None = None
    description: str | None = None
    is_active: bool | None = None

class AcceleratorInDB(Accelerator):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime