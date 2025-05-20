import os
import base64
import cv2
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

import tensorflow as tf
from models.models import Products
from routers.flowers import preprocess_image
from schemas.products import Product, ProductCreate, ProductUpdate
from controller.products import create_product as create_product_controller
from controller.products import get_product_by_id as get_product_by_id_controller
from controller.products import update_product as update_product_controller
from controller.products import delete_product as delete_product_controller
from config.db import get_db
from utils.paginator import paginate_dataframe

router = APIRouter(prefix="/products", tags=["Products"])

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")
# Load mô hình nhận diện hoa
model = tf.keras.models.load_model(MODEL_PATH) 
CLASS_NAMES = ['daisy', 'dandelion', 'rose', 'sunflower', 'tulip']
CONFIDENCE_THRESHOLD = 0.7
ENTROPY_THRESHOLD = 0.5

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    return create_product_controller(db=db, product_data=product_data, file=image_file)

@router.get("/", summary="Get a paginated list of all products with images in Base64")
def get_products(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    """
    Lấy danh sách sản phẩm với phân trang và trả về hình ảnh dưới dạng Base64.
    Hỗ trợ cả file ảnh có phần mở rộng .jpg và .png.
    """
    # Đường dẫn cơ sở cho hình ảnh
    BASE_MEDIA_PATH = "media/flowers/flowers_shop/"
    FLOWER_TYPE_MAP = {
        1: "daisy",
        2: "dandelion",
        3: "rose",
        4: "sunflower",
        5: "tulip"
    }

    # Lấy tất cả sản phẩm từ cơ sở dữ liệu
    products = db.query(Products).all()

    # Chuyển đổi danh sách sản phẩm thành dictionary
    products_data = []
    for product in products:
        product_dict = product.__dict__.copy()

        # Xây dựng đường dẫn hình ảnh dựa trên FlowerTypeID và ID sản phẩm
        if product.FlowerTypeID in FLOWER_TYPE_MAP:
            folder_name = FLOWER_TYPE_MAP[product.FlowerTypeID]
            image_path_jpg = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.jpg")
            image_path_png = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.png")

            # Kiểm tra file ảnh .jpg hoặc .png
            if os.path.isfile(image_path_jpg):
                with open(image_path_jpg, "rb") as image_file:
                    product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
            elif os.path.isfile(image_path_png):
                with open(image_path_png, "rb") as image_file:
                    product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
            else:
                product_dict["image_base64"] = None
        else:
            product_dict["image_base64"] = None

        products_data.append(product_dict)

    # Phân trang dữ liệu
    df = pd.DataFrame(products_data)
    paginated_result = paginate_dataframe(df, page=page, per_page=per_page)

    return {
        "data": paginated_result["data"],
        "total_records": paginated_result["total_record"],
        "page": paginated_result["page"],
        "per_page": paginated_result["per_page"]
    }

@router.get("/{product_id}", summary="Get a specific product by ID")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết của một sản phẩm và chuyển đổi hình ảnh thành Base64.
    """
    # Lấy sản phẩm từ cơ sở dữ liệu
    product = get_product_by_id_controller(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Đường dẫn cơ sở cho hình ảnh
    BASE_MEDIA_PATH = "media/flowers/flowers_shop/"
    FLOWER_TYPE_MAP = {
        1: "daisy",
        2: "dandelion",
        3: "rose",
        4: "sunflower",
        5: "tulip"
    }

    # Chuyển đổi sản phẩm thành dictionary
    product_dict = product.__dict__.copy()

    # Xây dựng đường dẫn hình ảnh dựa trên FlowerTypeID và ID sản phẩm
    if product.FlowerTypeID in FLOWER_TYPE_MAP:
        folder_name = FLOWER_TYPE_MAP[product.FlowerTypeID]
        image_path_jpg = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.jpg")
        image_path_png = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.png")

        # Kiểm tra file ảnh .jpg hoặc .png
        if os.path.isfile(image_path_jpg):
            with open(image_path_jpg, "rb") as image_file:
                product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
        elif os.path.isfile(image_path_png):
            with open(image_path_png, "rb") as image_file:
                product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
        else:
            product_dict["image_base64"] = None
    else:
        product_dict["image_base64"] = None

    return product_dict

@router.put("/{product_id}", response_model=Product, summary="Update a product")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin sản phẩm.
    """
    product = update_product_controller(db=db, product_id=product_id, product_data=product_data)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_200_OK, summary="Delete a product")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Xóa một sản phẩm.
    """
    product = delete_product_controller(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "Product deleted successfully", "deleted_id": product_id}

@router.post("/predict", summary="Predict flower type and get related products")
async def predict_product(
    file: UploadFile = File(...),
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """
    Dự đoán loài hoa từ ảnh được tải lên và lấy danh sách sản phẩm liên quan với phân trang.
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
        print(f"Predicted flower name: {flower_name}")

        # Map tên loài hoa với FlowerTypeID
        FLOWER_TYPE_MAP = {
            "daisy": 1,
            "dandelion": 2,
            "rose": 3,
            "sunflower": 4,
            "tulip": 5
        }
        flower_type_id = FLOWER_TYPE_MAP.get(flower_name.lower())
        print(f"Mapped FlowerTypeID: {flower_type_id}")

        if flower_type_id is None:
            raise HTTPException(status_code=400, detail=f"Loài hoa '{flower_name}' không nằm trong danh sách hỗ trợ")

        # Lấy danh sách sản phẩm liên quan dựa trên FlowerTypeID
        products = db.query(Products).filter(Products.FlowerTypeID == flower_type_id).all()
        print(f"Number of products found for FlowerTypeID {flower_type_id}: {len(products)}")

        if not products:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm nào cho loại hoa '{flower_name}'")

        # Chuyển đổi danh sách sản phẩm thành dictionary
        # Chuyển đổi danh sách sản phẩm thành dictionary
        # Chuyển đổi danh sách sản phẩm thành dictionary
        products_data = []
        BASE_MEDIA_PATH = "media/flowers/flowers_shop/"
        for product in products:
            product_dict = product.__dict__.copy()

            # Đọc file ảnh và mã hóa Base64
            folder_name = flower_name.lower()  # Sử dụng tên loài hoa (chữ) làm tên thư mục
            image_path_jpg = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.jpg")
            image_path_png = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.png")

            print(f"Checking image path JPG: {image_path_jpg}")
            print(f"File exists JPG: {os.path.isfile(image_path_jpg)}")
            print(f"Checking image path PNG: {image_path_png}")
            print(f"File exists PNG: {os.path.isfile(image_path_png)}")

            if os.path.isfile(image_path_jpg):
                with open(image_path_jpg, "rb") as image_file:
                    product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
                    print(f"Base64 encoded for product ID {product.id}: {product_dict['image_base64'][:30]}...")
            elif os.path.isfile(image_path_png):
                with open(image_path_png, "rb") as image_file:
                    product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
                    print(f"Base64 encoded for product ID {product.id}: {product_dict['image_base64'][:30]}...")
            else:
                product_dict["image_base64"] = None
                print(f"No image found for product ID: {product.id}")

            products_data.append(product_dict)

        # Phân trang dữ liệu
        df = pd.DataFrame(products_data)
        paginated_result = paginate_dataframe(df, page=page, per_page=per_page)

        # Tạo response
        response = {
            "flower_name": flower_name,
            "confidence": confidence,  # Độ tin cậy của dự đoán
            "related_products": paginated_result["data"],  # Danh sách sản phẩm liên quan
            "total_records": paginated_result["total_record"],
            "page": paginated_result["page"],
            "per_page": paginated_result["per_page"]
        }
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    
@router.get("/flower-type/{flower_type_id}", summary="Get products by flower type with pagination")
def get_products_by_flower_type(
    flower_type_id: int,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm theo loại hoa (FlowerTypeID) với phân trang.
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    # Tính toán offset
    skip = (page - 1) * per_page

    # Lấy tổng số sản phẩm theo loại hoa
    total_records = db.query(Products).filter(Products.FlowerTypeID == flower_type_id).count()

    # Lấy danh sách sản phẩm theo loại hoa với phân trang
    products_query = db.query(Products).filter(Products.FlowerTypeID == flower_type_id).offset(skip).limit(per_page).all()

    # Chuyển đổi danh sách sản phẩm thành dictionary và thêm Base64 cho ảnh
    BASE_MEDIA_PATH = "media/flowers/flowers_shop/"
    FLOWER_TYPE_MAP = {
        1: "daisy",
        2: "dandelion",
        3: "rose",
        4: "sunflower",
        5: "tulip"
    }

    products_data = []
    for product in products_query:
        product_dict = product.__dict__.copy()

        # Xây dựng đường dẫn hình ảnh
        if product.FlowerTypeID in FLOWER_TYPE_MAP:
            folder_name = FLOWER_TYPE_MAP[product.FlowerTypeID]
            image_path_jpg = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.jpg")
            image_path_png = os.path.join(BASE_MEDIA_PATH, folder_name, f"{product.id}.png")

            # Kiểm tra và mã hóa ảnh Base64
            if os.path.isfile(image_path_jpg):
                with open(image_path_jpg, "rb") as image_file:
                    product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
            elif os.path.isfile(image_path_png):
                with open(image_path_png, "rb") as image_file:
                    product_dict["image_base64"] = base64.b64encode(image_file.read()).decode("utf-8")
            else:
                product_dict["image_base64"] = None
        else:
            product_dict["image_base64"] = None

        products_data.append(product_dict)

    return {
        "data": products_data,
        "total_records": total_records,
        "page": page,
        "per_page": per_page
    }