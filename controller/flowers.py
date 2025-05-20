from sqlalchemy.orm import Session
from models.models import Flower as FlowerModel
from schemas.flowers import FlowerCreate, FlowerUpdate
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from utils.file_handler import save_image, delete_image
from config.db import MEDIA_ROOT, FLOWER_IMAGE_DIR_RELATIVE  
import logging

logger = logging.getLogger(__name__)

# --- CRUD Functions ---
# def get_flower_by_name(db: Session, flower_name: str) -> Optional[int]:
#     """
#     Truy vấn HoaID từ tên hoa trong cơ sở dữ liệu.
#     """
#     flower = db.query(FlowerModel).filter(FlowerModel.name == flower_name).first()
#     return flower.id if flower else None

# def get_products_by_flower_id(db: Session, hoa_id: int) -> List[dict]:


#     if hoa_id is None:
#         logger.warning("HoaID is None. Returning empty product list.")
#         return []

#     products = db.query(ProductModel).filter(ProductModel.flower_id == hoa_id).all()
#     if not products:
#         logger.info(f"No products found for HoaID {hoa_id}.")
#         return []

#     return [
#         {
#             "id": product.id,
#             "name": product.name,
#             "price": float(product.price),
#             "stock_quantity": product.stock_quantity,
#         }
#         for product in products
#     ]

def get_flower_details(db: Session, flower_name: str) -> dict:
    """
    Lấy thông tin chi tiết của hoa (description, image_path) từ cơ sở dữ liệu.
    """
    flower = db.query(FlowerModel).filter(FlowerModel.name == flower_name).first()
    if not flower:
        logger.warning(f"Flower with name '{flower_name}' not found.")
        return {
            "description": "Không có mô tả",
            "image_path": None
        }

    # Xây dựng đường dẫn ảnh đầy đủ
    image_url = f"/media/{flower.image_url}" if flower.image_url else None
    return {
        "description": flower.description or "Không có mô tả",
        "image_path": image_url
    }

def create_flower(db: Session, flower_data: FlowerCreate, image_file: Optional[UploadFile]) -> FlowerModel:
    saved_image_path = None
    if image_file:
        saved_image_path = save_image(image_file, flower_data.flower_type)  # Lưu ảnh theo loại hoa

    db_flower = FlowerModel(
        name=flower_data.name,
        description=flower_data.description,
        price=flower_data.price,
        stock_quantity=flower_data.stock_quantity,
        flower_type=flower_data.flower_type,
        image_url=saved_image_path
    )
    db.add(db_flower)
    db.commit()
    db.refresh(db_flower)
    return db_flower

def get_flower(db: Session, flower_id: int) -> FlowerModel:
    """Lấy thông tin flower theo ID."""
    flower = db.query(FlowerModel).filter(FlowerModel.id == flower_id).first()
    if not flower:
        logger.warning(f"Flower with ID {flower_id} not found.")
        raise HTTPException(status_code=404, detail="Flower not found")
    return flower

def get_flowers(db: Session, skip: int = 0, limit: int = 100) -> List[FlowerModel]:
    """Lấy danh sách flowers."""
    return db.query(FlowerModel).offset(skip).limit(limit).all()

def update_flower(db: Session, flower_id: int, flower_data: FlowerUpdate, image_file: Optional[UploadFile]) -> FlowerModel:
    """Cập nhật thông tin flower, có thể thay ảnh mới."""
    db_flower = get_flower(db, flower_id)

    update_data = flower_data.dict(exclude_unset=True)  # Chỉ lấy các trường được gửi lên
    new_image_path = None
    old_image_path = db_flower.image_url  # Lưu lại đường dẫn ảnh cũ

    if image_file:  # Nếu có ảnh mới được upload
        new_image_path = save_image(image_file, MEDIA_ROOT, FLOWER_IMAGE_DIR_RELATIVE)
        update_data['image_url'] = new_image_path  # Cập nhật image_url trong data sẽ set

    # Cập nhật các trường khác
    for key, value in update_data.items():
        setattr(db_flower, key, value)

    db.add(db_flower)  # Đánh dấu thay đổi
    db.commit()
    db.refresh(db_flower)

    # Nếu có ảnh mới được lưu thành công VÀ có ảnh cũ -> Xóa ảnh cũ
    if new_image_path and old_image_path:
        delete_image(old_image_path)

    logger.info(f"Updated flower {db_flower.id}. New image path: {new_image_path}")
    return db_flower

def delete_flower(db: Session, flower_id: int) -> int:
    """Xóa flower và ảnh liên quan."""
    db_flower = get_flower(db, flower_id)

    image_path_to_delete = db_flower.image_url  # Lấy đường dẫn ảnh trước khi xóa record
    flower_id_deleted = db_flower.id  # Lưu lại id để trả về

    db.delete(db_flower)
    db.commit()

    # Xóa file ảnh sau khi commit thành công
    delete_image(image_path_to_delete)

    logger.info(f"Deleted flower {flower_id_deleted}. Associated image path: {image_path_to_delete}")
    return flower_id_deleted