from pydantic import BaseModel

class DatasetCreate(BaseModel):
    name: str
    description: str

class DatasetResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_email: str

    class Config:
        from_attributes = True