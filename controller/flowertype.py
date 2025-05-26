from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.flowertype import FlowerTypeCreate
from models.models_db import FlowerTypes

def create_flower_type(db: Session, flower_type: FlowerTypeCreate) -> FlowerTypes:
    db_flower_type = FlowerTypes(Name=flower_type.Name, Description=flower_type.Description)
    db.add(db_flower_type)
    db.commit()
    db.refresh(db_flower_type)
    return db_flower_type

def get_flower_types(db: Session, skip: int = 0, limit: int = 100) -> List[FlowerTypes]:
    return db.query(FlowerTypes).offset(skip).limit(limit).all()

def get_flower_type_by_id(db: Session, flower_type_id: int) -> Optional[FlowerTypes]:
    return db.query(FlowerTypes).filter(FlowerTypes.id == flower_type_id).first()

def update_flower_type(db: Session, flower_type_id: int, flower_type_data: FlowerTypeCreate) -> Optional[FlowerTypes]:
    db_flower_type = get_flower_type_by_id(db, flower_type_id)
    if db_flower_type:
        db_flower_type.Name = flower_type_data.Name
        db_flower_type.Description = flower_type_data.Description
        db.commit()
        db.refresh(db_flower_type)
    return db_flower_type

def delete_flower_type(db: Session, flower_type_id: int) -> Optional[FlowerTypes]:
    db_flower_type = get_flower_type_by_id(db, flower_type_id)
    if db_flower_type:
        db.delete(db_flower_type)
        db.commit()
        return db_flower_type
    return None
