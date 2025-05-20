from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from config.db import get_db
from schemas.categories import Category as CategorySchema, CategoryCreate
from controller.categories import create_category, get_category_by_id, get_categories, update_category, delete_category
from utils.paginator import paginate_dataframe
import pandas as pd

router = APIRouter(prefix="/categories")

@router.get("/", status_code=status.HTTP_200_OK)
async def read_categories(request: Request, db: Session = Depends(get_db)):
    try:
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        
        all_categories = get_categories(db, skip=0, limit=1000)
        df = pd.DataFrame([{
            "id": cat.id,
            "Name": cat.Name,
            "Description": cat.Description
        } for cat in all_categories])
        
        return paginate_dataframe(df, page, per_page)
    
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Page and per_page must be integers")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{id}", response_model=CategorySchema)
async def read_category(id: int, db: Session = Depends(get_db)):
    category = get_category_by_id(db, category_id=id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategorySchema)
async def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, category=category)

@router.put("/{id}", response_model=CategorySchema)
async def update_category_endpoint(id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = update_category(db, category_id=id, category_data=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/{id}", response_model=CategorySchema)
async def delete_category_endpoint(id: int, db: Session = Depends(get_db)):
    db_category = delete_category(db, category_id=id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category