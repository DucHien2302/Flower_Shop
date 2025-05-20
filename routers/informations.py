from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.authentication import get_user_dependency
from config.db import get_db
from schemas.informations import CreateInformation, UpdateInformation
from controller.informations import create_information, update_information, get_information_by_user_id
from globals import sessions

router = APIRouter(
    prefix="/informations"
)

@router.get("/info")
async def read_information(
        db: Session = Depends(get_db),
        user_id: int = Depends(get_user_dependency(sessions))
    ):
    information = get_information_by_user_id(db, user_id)
    if information is None:
        raise HTTPException(status_code=404, detail="Information not found")
    return information

@router.post("/")
async def create_information_endpoint(
        information: CreateInformation, 
        db: Session = Depends(get_db),
        user_id: int = Depends(get_user_dependency(sessions))
    ):
    db_information = create_information(db, information, user_id)
    if db_information is None:
        raise HTTPException(status_code=400, detail="Information already exists")
    return db_information

@router.put("/{id}")
async def update_information_endpoint(
        info_id: int,
        information: UpdateInformation, 
        db: Session = Depends(get_db),
        user_id: int = Depends(get_user_dependency(sessions))
    ):
    db_information = update_information(db, info_id, information)
    if db_information is None:
        raise HTTPException(status_code=404, detail="Information not found")
    return db_information
