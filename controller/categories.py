from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.categories import CategoryCreate
from models.models import Categories

def create_category(db: Session, category: CategoryCreate) -> Categories:
    db_category = Categories(
        Name=category.Name,
        Description=category.Description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Categories]:
    return db.query(Categories).offset(skip).limit(limit).all()

def get_category_by_id(db: Session, category_id: int) -> Optional[Categories]:
    return db.query(Categories).filter(Categories.id == category_id).first()

def update_category(db: Session, category_id: int, category_data: CategoryCreate) -> Optional[Categories]:
    db_category = get_category_by_id(db, category_id)
    if db_category:
        db_category.Name = category_data.Name
        db_category.Description = category_data.Description
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Optional[Categories]:
    db_category = get_category_by_id(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return db_category
    return None