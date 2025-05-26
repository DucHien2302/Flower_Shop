from sqlalchemy.orm import Session
from models.models_db import Carts
from schemas.carts import CartItem, CartResponse
from sqlalchemy import text

def add_cart_item(
    db: Session,
    item: CartItem,
    cart_id: str
):
    cart_item = db.query(Carts).filter(
        Carts.CartId == cart_id,
        Carts.ProductId == item.product_id
    ).first()
    if cart_item:
        cart_item.Quantity += item.quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item
    db_item = Carts(
        CartId=cart_id,
        ProductId=item.product_id,
        Quantity=item.quantity,
        IsChecked=0,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_cart_item(
    db: Session,
    cart_id: str,
    product_id: int
):
    db_item = db.query(Carts).filter(
        Carts.CartId == cart_id,
        Carts.ProductId == product_id
    ).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def update_cart_item(
    db: Session,
    cart_id: str,
    product_id: int,
    quantity: int
):
    db_item = db.query(Carts).filter(
        Carts.CartId == cart_id,
        Carts.ProductId == product_id
    ).first()
    if db_item:
        db_item.Quantity = quantity
        db.commit()
        db.refresh(db_item)
        return db_item
    return None

def update_cart_item_selected(
    db: Session,
    cart_id: str,
    product_id: int
):
    db_item = db.query(Carts).filter(
        Carts.CartId == cart_id,
        Carts.ProductId == product_id
    ).first()
    if db_item:
        db_item.IsChecked = 1 if db_item.IsChecked == 0 else 0
        db.commit()
        db.refresh(db_item)
        return db_item
    return None

def get_cart_items(
    db: Session,
    cart_id: str
):
    sql = text("CALL GetCartsById(:p_CartId)")
    result = db.execute(sql, {"p_CartId": cart_id})
    db_items = result.fetchall()
    cart_responses = []
    for item in db_items:
        cart_responses.append(
            CartResponse(
                ProductId=item[0],
                Name=item[1],
                ImageURL=item[2],
                Quantity=item[3],
                Price=item[4],
                Amount=item[5],
                FlowerTypeID=item[6],
                IsChecked=item[7]
            )
        )
    return cart_responses

def get_cart_items_is_checked(
    db: Session,
    cart_id: str
):
    db_items = db.query(Carts).filter(
        Carts.CartId == cart_id,
        Carts.IsChecked == 1
    ).all()
    return db_items