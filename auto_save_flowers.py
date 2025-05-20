import os
import random
from sqlalchemy.orm import Session
from models.models import Flower as FlowerModel
from config.db import FLOWER_TYPE_DIRS, get_db
from decimal import Decimal

def auto_save_flowers_from_images(db: Session):
    """
    Tự động lưu thông tin hoa vào cơ sở dữ liệu dựa trên các hình ảnh có sẵn trong thư mục media/flowers/<flower_type>.
    """
    for flower_type, folder_path in FLOWER_TYPE_DIRS.items():
        if not os.path.exists(folder_path):
            print(f"Folder not found for flower type '{flower_type}': {folder_path}")
            continue

        # Duyệt qua tất cả các file trong thư mục
        flower_count = 1  # Đếm số lượng hoa để đặt tên
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Bỏ qua nếu không phải file
            if not os.path.isfile(file_path):
                continue

            # Tạo dữ liệu mẫu cho mỗi hình ảnh
            flower_name = f"{flower_type.capitalize()} {flower_count}"  # Tên hoa theo định dạng "Daisy 1", "Daisy 2", ...
            description = f"A beautiful {flower_type} flower."
            price = Decimal(random.uniform(5.0, 20.0)).quantize(Decimal("0.01"))  # Giá ngẫu nhiên từ 5.00 đến 20.00
            stock_quantity = random.randint(10, 100)  # Số lượng ngẫu nhiên từ 10 đến 100
            image_url = os.path.relpath(file_path, start=os.path.join(FLOWER_TYPE_DIRS[flower_type], ".."))

            # Kiểm tra xem bản ghi đã tồn tại chưa (dựa trên image_url)
            existing_flower = db.query(FlowerModel).filter(FlowerModel.image_url == image_url).first()
            if existing_flower:
                print(f"Flower with image '{image_url}' already exists. Skipping...")
                continue

            # Tạo bản ghi mới
            new_flower = FlowerModel(
                name=flower_name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                flower_type=flower_type,
                image_url=image_url
            )
            db.add(new_flower)
            print(f"Added flower: {flower_name} with image '{image_url}'")

            flower_count += 1  # Tăng số thứ tự hoa

    # Commit tất cả thay đổi vào cơ sở dữ liệu
    db.commit()
    print("All flowers have been added to the database.")

# Sử dụng hàm
if __name__ == "__main__":
    with next(get_db()) as db:
        auto_save_flowers_from_images(db)