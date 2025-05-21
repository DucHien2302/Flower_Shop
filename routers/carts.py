from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from config.db import get_db
from schemas.carts import CartItem, CartDelete, CartSelected
from controller.carts import get_cart_items, add_cart_item, delete_cart_item, update_cart_item, update_cart_item_selected

router = APIRouter(
    prefix="/carts"
)

@router.get("/")
async def get_cart(
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")
        else:
            cart_items = get_cart_items(db, session_id)
            return cart_items
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/")
async def add_cart(
    item: CartItem,
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            session_id = str(uuid.uuid4()).replace("-", "")
            db_item = add_cart_item(db, item, session_id)
            response = JSONResponse(content=db_item)
            response.set_cookie(key="session_id", value=session_id, httponly=True)
            return response
        else:
            db_item = add_cart_item(db, item, session_id)
            return db_item
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/")
async def delete_cart(
    item: CartDelete,
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")
        else:
            db_item = delete_cart_item(db, session_id, item.product_id)
            if db_item:
                return {"message": "Item deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Item not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.put("/")
async def update_cart(
    item: CartItem,
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")
        else:
            db_item = update_cart_item(db, session_id, item.product_id, item.quantity)
            if db_item:
                return db_item
            else:
                raise HTTPException(status_code=404, detail="Item not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.put("/selected")
async def update_cart_selected(
    item: CartSelected,
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")
        else:
            db_item = update_cart_item_selected(db, session_id, item.product_id)
            if db_item:
                return db_item
            else:
                raise HTTPException(status_code=404, detail="Item not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")