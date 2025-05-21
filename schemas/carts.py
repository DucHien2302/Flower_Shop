from pydantic import BaseModel

class CartItem(BaseModel):
    product_id: int
    quantity: int

class CartProId(BaseModel):
    product_id: int

class CartDelete(CartProId):
    pass

class CartSelected(CartProId):
    pass

class CartResponse(BaseModel):
    ProductId: int
    Name: str
    ImageURL: str
    StockQuantity: int
    Price: float
    Amount: float
    FlowerTypeID: int
    IsChecked: int