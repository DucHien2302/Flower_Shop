from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from config.db import get_db
from schemas.flowertype import FlowerType as FlowerTypeSchema, FlowerTypeCreate  # This should work
from controller.flowertype import create_flower_type, get_flower_type_by_id, get_flower_types, update_flower_type, delete_flower_type
from utils.paginator import paginate_dataframe
import pandas as pd

router = APIRouter(prefix="/flowertypes")

@router.get("/", status_code=status.HTTP_200_OK)
async def read_flower_types(request: Request, db: Session = Depends(get_db)):
    try:
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        
        flower_types = get_flower_types(db, skip=0, limit=1000)
        df = pd.DataFrame([{
            "id": ft.id,
            "Name": ft.Name,
            "Description": ft.Description
        } for ft in flower_types])
        
        return paginate_dataframe(df, page, per_page)
    
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Page and per_page must be integers")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{id}", response_model=FlowerTypeSchema)
async def read_flower_type(id: int, db: Session = Depends(get_db)):
    flower_type = get_flower_type_by_id(db, flower_type_id=id)
    if flower_type is None:
        raise HTTPException(status_code=404, detail="Flower type not found")
    return flower_type

@router.post("/", response_model=FlowerTypeSchema)
async def create_flower_type_endpoint(flower_type: FlowerTypeCreate, db: Session = Depends(get_db)):
    return create_flower_type(db, flower_type=flower_type)

@router.put("/{id}", response_model=FlowerTypeSchema)
async def update_flower_type_endpoint(id: int, flower_type: FlowerTypeCreate, db: Session = Depends(get_db)):
    db_flower_type = update_flower_type(db, flower_type_id=id, flower_type_data=flower_type)
    if db_flower_type is None:
        raise HTTPException(status_code=404, detail="Flower type not found")
    return db_flower_type

@router.delete("/{id}", response_model=FlowerTypeSchema)
async def delete_flower_type_endpoint(id: int, db: Session = Depends(get_db)):
    db_flower_type = delete_flower_type(db, flower_type_id=id)
    if db_flower_type is None:
        raise HTTPException(status_code=404, detail="Flower type not found")
    return db_flower_type

