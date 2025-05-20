from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# Cập nhật chuỗi kết nối để bao gồm mật khẩu
engine = create_engine("mysql+pymysql://root:root@localhost:3306/DoAnPython")
meta = MetaData()
conn = engine.connect()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Đường dẫn gốc của dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cấu hình thư mục media
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
FLOWER_IMAGE_DIR_RELATIVE = "flowers"  # Đường dẫn tương đối cho ảnh hoa
FLOWER_IMAGE_DIR_ABSOLUTE = os.path.join(MEDIA_ROOT, FLOWER_IMAGE_DIR_RELATIVE)

# Các thư mục con cho từng loại hoa
FLOWER_TYPE_DIRS = {
    "daisy": os.path.join(FLOWER_IMAGE_DIR_ABSOLUTE, "daisy"),
    "dandelion": os.path.join(FLOWER_IMAGE_DIR_ABSOLUTE, "dandelion"),
    "rose": os.path.join(FLOWER_IMAGE_DIR_ABSOLUTE, "rose"),
    "sunflower": os.path.join(FLOWER_IMAGE_DIR_ABSOLUTE, "sunflower"),
    "tulip": os.path.join(FLOWER_IMAGE_DIR_ABSOLUTE, "tulip"),
}

# Tạo các thư mục nếu chưa tồn tại
for dir_path in FLOWER_TYPE_DIRS.values():
    os.makedirs(dir_path, exist_ok=True)