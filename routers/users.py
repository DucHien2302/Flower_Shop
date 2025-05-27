from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
import uuid
from sqlalchemy.orm import Session
from config.db import get_db
from models.models_db import SysUser
from schemas.users import UserAuth
from controller.users import create_user, authenticate_user
from globals import sessions

router = APIRouter(
    prefix="/users"
)

@router.post("/register")
async def create_user_endpoint(user: UserAuth, db: Session = Depends(get_db)):
    user_exists = db.query(SysUser).filter(SysUser.Email == user.email).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email is existed")
    db_user = create_user(db, user=user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User already registered")
    return {"Message": "Register Successfully"}

@router.post("/login")
async def login(
    user: UserAuth, 
    db: Session = Depends(get_db),
    session_id: str = Cookie(None)
):
    db_user = authenticate_user(db, user=user)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if session_id is None:
        session_id = str(uuid.uuid4()).replace("-", "")
    
    sessions[session_id] = db_user.id
    response = JSONResponse(content={"session_id": session_id, "user_id": db_user.id, "isSuccess": True, "message": "Login successful"})
    if session_id is not None:
        response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                samesite="None",  # hoặc "Lax", tùy luồng auth
                secure=True,       # bắt buộc với samesite=None
                max_age=60*60*24
            )
    return response

@router.post("/logout")
async def logout(
        session_id: str = Cookie(None)
    ):
    if session_id is None:
        raise HTTPException(status_code=401, detail="No session ID provided")
    
    if session_id not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    del sessions[session_id]
    
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(
        key="session_id", 
        httponly=True,
        samesite="None",
        secure=True
    )
    return response