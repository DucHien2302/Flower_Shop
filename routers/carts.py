import base64
import os
from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from config.db import get_db
from models.models_db import Carts
from schemas.carts import CartItem, CartSelected
from controller.carts import get_cart_items, add_cart_item, update_cart_item, update_cart_item_selected, get_cart_items_is_checked

router = APIRouter(
    prefix="/carts"
)

BASE_MEDIA_PATH = "media/flowers/flowers_shop/"
FLOWER_TYPE_MAP = {
    1: "daisy",
    2: "dandelion",
    3: "rose",
    4: "sunflower",
    5: "tulip"
}

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
            for item in cart_items:
                # Xây dựng đường dẫn hình ảnh dựa trên FlowerTypeID và ID sản phẩm
                if item.FlowerTypeID in FLOWER_TYPE_MAP:
                    folder_name = FLOWER_TYPE_MAP[item.FlowerTypeID]
                    image_path_jpg = os.path.join(BASE_MEDIA_PATH, folder_name, f"{item.ProductId}.jpg")
                    image_path_png = os.path.join(BASE_MEDIA_PATH, folder_name, f"{item.ProductId}.png")

                # Kiểm tra file ảnh .jpg hoặc .png
                if os.path.isfile(image_path_jpg):
                    with open(image_path_jpg, "rb") as image_file:
                        item.ImageURL = base64.b64encode(image_file.read()).decode("utf-8")
                elif os.path.isfile(image_path_png):
                    with open(image_path_png, "rb") as image_file:
                        item.ImageURL = base64.b64encode(image_file.read()).decode("utf-8")
            return cart_items
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/is-checked")
async def get_cart_is_checked(
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")
        else:
            cart_items = get_cart_items_is_checked(db, session_id)
            for item in cart_items:
                # Xây dựng đường dẫn hình ảnh dựa trên FlowerTypeID và ID sản phẩm
                if item.FlowerTypeID in FLOWER_TYPE_MAP:
                    folder_name = FLOWER_TYPE_MAP[item.FlowerTypeID]
                    image_path_jpg = os.path.join(BASE_MEDIA_PATH, folder_name, f"{item.ProductId}.jpg")
                    image_path_png = os.path.join(BASE_MEDIA_PATH, folder_name, f"{item.ProductId}.png")

                # Kiểm tra file ảnh .jpg hoặc .png
                if os.path.isfile(image_path_jpg):
                    with open(image_path_jpg, "rb") as image_file:
                        item.ImageURL = base64.b64encode(image_file.read()).decode("utf-8")
                elif os.path.isfile(image_path_png):
                    with open(image_path_png, "rb") as image_file:
                        item.ImageURL = base64.b64encode(image_file.read()).decode("utf-8")
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
            item_dict = {k: v for k, v in db_item.__dict__.items() if not k.startswith("_")}
            response = JSONResponse(content=item_dict)
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                samesite="None",  # hoặc "Lax", tùy luồng auth
                secure=True,       # bắt buộc với samesite=None
                max_age=60*60*24
            )
            return response
        else:
            db_item = add_cart_item(db, item, session_id)
            return db_item
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/{id}")
async def delete_cart(
    id: int,  # truyền vào từ URL
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    try:
        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID not found")

        db_item = db.query(Carts).filter(
            Carts.CartId == session_id,
            Carts.ProductId == id
        ).first()

        if db_item:
            db.delete(db_item)
            db.commit()
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