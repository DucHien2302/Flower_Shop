import os
import shutil
from uuid import uuid4
from fastapi import UploadFile, HTTPException
import logging
from config.db import FLOWER_TYPE_DIRS, MEDIA_ROOT

logger = logging.getLogger(__name__)

def ensure_dir(directory: str):
    os.makedirs(directory, exist_ok=True)

def save_image(upload_file: UploadFile, flower_type: str) -> str:
    """
    Lưu file ảnh vào thư mục tương ứng với loại hoa.
    Trả về đường dẫn tương đối của file đã lưu.
    """
    if flower_type not in FLOWER_TYPE_DIRS:
        raise HTTPException(status_code=400, detail=f"Invalid flower type: {flower_type}")

    flower_dir = FLOWER_TYPE_DIRS[flower_type]

    ext = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid4()}{ext}"
    relative_path = os.path.join("flowers", flower_type, unique_filename)
    absolute_path = os.path.join(flower_dir, unique_filename)

    try:
        # Lưu file
        with open(absolute_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return relative_path
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        raise HTTPException(status_code=500, detail="Could not save image file")
    finally:
        upload_file.file.close()

def delete_image(relative_path: str):
    """Xóa file ảnh dựa vào đường dẫn tương đối."""
    if not relative_path:
        return
    absolute_path = os.path.join(MEDIA_ROOT, relative_path)
    if os.path.isfile(absolute_path):
        try:
            os.remove(absolute_path)
            logger.info(f"Deleted image file: {absolute_path}")
        except Exception as e:
            logger.error(f"Error deleting image file {absolute_path}: {e}")
    else:
        logger.warning(f"Image file not found for deletion: {absolute_path}")