from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class FlowerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)
    flower_type: str = Field(..., pattern="^(daisy|dandelion|rose|sunflower|tulip)$")  # Chỉ nhận các giá trị hợp lệ

class FlowerCreate(FlowerBase):
    pass

class FlowerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    flower_type: Optional[str] = Field(None, pattern="^(daisy|dandelion|rose|sunflower|tulip)$")

class Flower(FlowerBase):
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True