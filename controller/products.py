import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.products import ProductCreate, ProductUpdate
from models.models import Products

def create_product(db: Session, product_data: ProductCreate, file: UploadFile) -> Products:
    try:
        # Đường dẫn thư mục lưu trữ hình ảnh dựa trên FlowerTypeID
        BASE_MEDIA_PATH = "media/flowers/flowers_shop/"
        flower_type_map = {
            1: "Daisy",
            2: "Dandelion",
            3: "Rose",
            4: "Sunflower",
            5: "Tulip"
        }
        folder_name = flower_type_map.get(product_data.FlowerTypeID, "Unknown")
        folder_path = os.path.join(BASE_MEDIA_PATH, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Tạo sản phẩm mới (chưa lưu hình ảnh)
        db_product = Products(
            Name=product_data.Name,
            Description=product_data.Description,
            Price=product_data.Price,
            DiscountedPrice=product_data.DiscountedPrice,
            StockQuantity=product_data.StockQuantity,
            CategoryID=product_data.CategoryID,
            FlowerTypeID=product_data.FlowerTypeID,
            ImageURL="",  # Tạm thời để trống
            IsFreeship=product_data.IsFreeship
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Lưu file vào thư mục với tên là mã ID của sản phẩm
        file_extension = os.path.splitext(file.filename)[1]  # Lấy phần mở rộng của file (vd: .jpg, .png)
        file_name = f"{db_product.id}{file_extension}"  # Tên file là ID của sản phẩm
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Cập nhật đường dẫn hình ảnh vào sản phẩm
        db_product.ImageURL = file_path
        db.commit()
        db.refresh(db_product)

        return db_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Products]:
    return db.query(Products).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Optional[Products]:
    """
    Lấy thông tin chi tiết của một sản phẩm dựa trên ID.
    """
    return db.query(Products).filter(Products.id == product_id).first()

def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Products]:
    """
    Cập nhật thông tin sản phẩm.
    """
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db_product.Name = product_data.Name
        db_product.Description = product_data.Description
        db_product.Price = product_data.Price
        db_product.DiscountedPrice = product_data.DiscountedPrice
        db_product.StockQuantity = product_data.StockQuantity
        db_product.CategoryID = product_data.CategoryID
        db_product.FlowerTypeID = product_data.FlowerTypeID
        db_product.ImageURL = product_data.ImageURL
        db_product.IsFreeship = product_data.IsFreeship
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> Optional[Products]:
    """
    Xóa một sản phẩm dựa trên ID.
    """
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return db_product
    return None