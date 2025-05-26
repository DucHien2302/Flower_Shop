import os
from fastapi import (
    APIRouter, Depends, HTTPException, status,
    UploadFile, File, Form
)
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import logging
import pandas as pd
import base64
# Import các module cần thiết
import controller.flowers as crud
import schemas.flowers as schemas
from config.db import FLOWER_TYPE_DIRS, get_db
from utils.paginator import paginate_dataframe
from typing import List, Dict
import tensorflow as tf
import cv2
import numpy as np
from schemas.flowers import FlowerBase
from models.models_db import Flower as FlowerModel
from dotenv import load_dotenv

# Cấu hình logger
logger = logging.getLogger(__name__)

# Khởi tạo router
router = APIRouter(prefix="/flowers", tags=["Flowers"])

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")
# Load mô hình nhận diện hoa
model = tf.keras.models.load_model(MODEL_PATH) 
CLASS_NAMES = ['daisy', 'dandelion', 'rose', 'sunflower', 'tulip']
CONFIDENCE_THRESHOLD = 0.7
ENTROPY_THRESHOLD = 0.5

# --- Endpoint CREATE ---

def preprocess_image(img: np.ndarray, target_size=(224, 224), normalize=True) -> np.ndarray:
    if img is None:
        raise ValueError("Ảnh đầu vào không hợp lệ")
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    if normalize:
        img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

# Endpoint: Dự đoán loài hoa từ ảnh
# @router.post("/predict", response_model=Dict)
# async def predict_flower(file: UploadFile = File(...)):
#     try:
#         contents = await file.read()
#         nparray = np.frombuffer(contents, np.uint8)
#         img = cv2.imdecode(nparray, cv2.IMREAD_COLOR)
        
#         if img is None:
#             raise HTTPException(status_code=400, detail="Không thể giải mã ảnh từ dữ liệu tải lên")

#         # Tiền xử lý ảnh
#         img_processed = preprocess_image(img)

#         # Dự đoán
#         predictions = model.predict(img_processed, verbose=0)
#         predicted_class = np.argmax(predictions[0])
#         confidence = float(predictions[0][predicted_class])

#         # Tính entropy để kiểm tra độ chắc chắn
#         entropy = -np.sum(predictions[0] * np.log(predictions[0] + 1e-10))
        
#         # Kiểm tra độ tin cậy và entropy
#         if confidence < CONFIDENCE_THRESHOLD or entropy > ENTROPY_THRESHOLD:
#             raise HTTPException(status_code=400, detail="Không thể nhận diện loài hoa / Vật thể từ ảnh này")

#         flower_name = CLASS_NAMES[predicted_class]

#         # Lấy thông tin chi tiết và sản phẩm
#         flower_details = crud.get_flower_details(flower_name)
#         hoa_id =  crud.get_flower_by_name(flower_name)
#         products =  crud.get_products_by_flower_id(hoa_id) if hoa_id else []

#         response = {
#             "flower_name": flower_name,
#             "confidence": confidence,  # Thêm độ tin cậy vào response
#             "description": flower_details["description"],
#             "image_path": flower_details["image_path"],
#             "products": products
#         }
#         return response

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
@router.post("/predict", response_model=Dict)
async def predict_flower(
    file: UploadFile = File(...),
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """
    Dự đoán loài hoa từ ảnh được tải lên và lấy dữ liệu liên quan với phân trang.
    """
    try:
        # Đọc nội dung file và chuyển đổi thành ảnh
        contents = await file.read()
        nparray = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparray, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Không thể giải mã ảnh từ dữ liệu tải lên")

        # Tiền xử lý ảnh
        img_processed = preprocess_image(img)

        # Dự đoán
        predictions = model.predict(img_processed, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])

        # Tính entropy để kiểm tra độ chắc chắn
        entropy = -np.sum(predictions[0] * np.log(predictions[0] + 1e-10))

        # Kiểm tra độ tin cậy và entropy
        if confidence < CONFIDENCE_THRESHOLD or entropy > ENTROPY_THRESHOLD:
            raise HTTPException(status_code=400, detail="Không thể nhận diện loài hoa / Vật thể từ ảnh này")

        # Lấy tên loài hoa dự đoán
        flower_name = CLASS_NAMES[predicted_class]
        flowers = db.query(FlowerModel).filter(FlowerModel.flower_type == flower_name).all()

        # Chuyển đổi danh sách hoa thành dictionary
        flowers_data = []
        for flower in flowers:
            flower_dict = {
                "id": flower.id,
                "name": flower.name,
                "description": flower.description,
                "price": float(flower.price),
                "stock_quantity": flower.stock_quantity,
                "flower_type": flower.flower_type,
                "image_url": flower.image_url,
                "created_at": flower.created_at,
                "updated_at": flower.updated_at
            }

            # Đọc file ảnh và mã hóa Base64
            image_path = os.path.join(FLOWER_TYPE_DIRS[flower.flower_type], os.path.basename(flower.image_url)) if flower.image_url else None
            if image_path and os.path.isfile(image_path):
                with open(image_path, "rb") as image_file:
                    flower_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
            else:
                flower_dict["image_base64"] = None

            flowers_data.append(flower_dict)

        # Phân trang dữ liệu
        df = pd.DataFrame(flowers_data)
        paginated_result = paginate_dataframe(df, page=page, per_page=per_page)

        # Tạo response
        response = {
            "flower_name": flower_name,
            "confidence": confidence,  # Độ tin cậy của dự đoán
            "related_flowers": paginated_result["data"],  # Danh sách hoa liên quan
            "total_records": paginated_result["total_record"],
            "page": paginated_result["page"],
            "per_page": paginated_result["per_page"]
        }
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /predict: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@router.post("/", response_model=schemas.Flower, status_code=status.HTTP_201_CREATED)
def create_flower(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: Decimal = Form(...),
    stock_quantity: int = Form(...),
    flower_type: str = Form(...), 
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if flower_type not in FLOWER_TYPE_DIRS:
        raise HTTPException(status_code=400, detail=f"Invalid flower type: {flower_type}")

    flower_data = schemas.FlowerCreate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        flower_type=flower_type
    )
    return crud.create_flower(db=db, flower_data=flower_data, image_file=image_file)

@router.get("/", summary="Get a paginated list of all flowers")
def handle_read_flowers(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    """
    Retrieves a paginated list of flowers with images encoded in Base64.
    """
    flowers = crud.get_flowers(db)

    flowers_data = []
    for flower in flowers:
        flower_dict = flower.__dict__.copy()

        # Đọc file ảnh và mã hóa Base64
        image_path = os.path.join(FLOWER_TYPE_DIRS[flower.flower_type], os.path.basename(flower.image_url)) if flower.image_url else None
        if image_path and os.path.isfile(image_path):
            with open(image_path, "rb") as image_file:
                flower_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
        else:
            flower_dict["image_base64"] = None

        flowers_data.append(flower_dict)

    df = pd.DataFrame(flowers_data)

    paginated_result = paginate_dataframe(df, page=page, per_page=per_page)

    return {
        "data": paginated_result["data"],
        "total_records": paginated_result["total_record"],
        "page": paginated_result["page"],
        "per_page": paginated_result["per_page"]
    }
# --- Endpoint GET ONE ---
@router.get("/{flower_id}", response_model=schemas.Flower, summary="Get a specific flower by ID")
def handle_read_flower(flower_id: int, db: Session = Depends(get_db)):
    """
    Retrieves details for a specific flower with its image encoded in Base64.
    """
    db_flower = crud.get_flower(db, flower_id=flower_id)
    if db_flower is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")

    flower_dict = db_flower.__dict__.copy()

    # Đọc file ảnh và mã hóa Base64
    image_path = os.path.join(FLOWER_TYPE_DIRS[db_flower.flower_type], os.path.basename(db_flower.image_url)) if db_flower.image_url else None
    if image_path and os.path.isfile(image_path):
        with open(image_path, "rb") as image_file:
            flower_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
    else:
        flower_dict["image_base64"] = None

    return flower_dict

@router.put(
    "/{flower_id}",
    response_model=schemas.Flower,
    summary="Update a flower with optional new image"
)
def handle_update_flower(
    flower_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[Decimal] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    flower_type: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None, description="New flower image file (optional)"),
    db: Session = Depends(get_db)
):
    """
    Updates an existing flower. Provide fields to update as form data.
    Optionally upload a new image file to replace the existing one.
    """
    update_data_dict = {}
    if name is not None: update_data_dict['name'] = name
    if description is not None: update_data_dict['description'] = description
    if price is not None: update_data_dict['price'] = price
    if stock_quantity is not None: update_data_dict['stock_quantity'] = stock_quantity
    if flower_type is not None: update_data_dict['flower_type'] = flower_type

    if not update_data_dict and not image_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data or image provided."
        )

    flower_update_schema = schemas.FlowerUpdate(**update_data_dict)

    try:
        updated_flower = crud.update_flower(
            db=db,
            flower_id=flower_id,
            flower_data=flower_update_schema,
            image_file=image_file
        )
        if updated_flower is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")
        return updated_flower
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating flower {flower_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error updating flower.")

@router.delete(
    "/{flower_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a flower and its associated image"
)
def handle_delete_flower(flower_id: int, db: Session = Depends(get_db)):
    """
    Deletes a flower record and its corresponding image file from the server.
    """
    try:
        deleted_flower_id = crud.delete_flower(db=db, flower_id=flower_id)
        if deleted_flower_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flower not found")
        return {"message": "Flower deleted successfully", "deleted_id": deleted_flower_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting flower {flower_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error deleting flower.")

