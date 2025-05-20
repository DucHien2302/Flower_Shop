from pydantic import BaseModel

class FlowerTypeBase(BaseModel):
    Name: str
    Description: str = None

class FlowerTypeCreate(FlowerTypeBase):
    pass

class FlowerType(FlowerTypeBase):
    id: int

    class Config:
        from_attributes = True
        