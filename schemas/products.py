from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    Name: str
    Description: Optional[str] = None
    Price: int
    DiscountedPrice: Optional[int] = None
    StockQuantity: Optional[int] = 0
    CategoryID: Optional[int] = None
    ImageURL: Optional[str] = None
    IsFreeship: Optional[bool] = False
    FlowerTypeID: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    Name: Optional[str] = None
    Description: Optional[str] = None
    Price: Optional[int] = None
    DiscountedPrice: Optional[int] = None
    StockQuantity: Optional[int] = None
    CategoryID: Optional[int] = None
    ImageURL: Optional[str] = None
    IsFreeship: Optional[bool] = None
    FlowerTypeID: Optional[int] = None

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True