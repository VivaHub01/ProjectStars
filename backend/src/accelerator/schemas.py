from pydantic import BaseModel


class Accelerator(BaseModel):
    university: str
    description: str | None = None
    is_active: bool = True

class AcceleratorCreate(Accelerator):
    pass

class AcceleratorUpdate(BaseModel):
    university: str | None = None
    description: str | None = None
    is_active: bool

class AcceleratorInDB(Accelerator):
    id: int