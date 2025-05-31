from sqlalchemy.orm import Session
from models.models_db import Informations as Info, SysUser
from schemas.informations import CreateInformation, UpdateInformation, ResponseInformation

def create_information(
        db: Session, 
        information: CreateInformation,
        user_id: int,
    ): 
    db_information = db.query(Info).filter(Info.UserId == user_id).first()
    if db_information:
        return None
    db_information = Info(
        FirstName=information.first_name,
        LastName=information.last_name,
        FullName=information.first_name + " " + information.last_name,
        DateOfBirth=information.date_of_birth,
        Address=information.address,
        Gender=information.gender,
        UserId=user_id
    )
    db.add(db_information)
    db.commit()
    db.refresh(db_information)
    return db_information

def update_information(
        db: Session, 
        user_id: int,
        information: UpdateInformation
    ):
    db_information = db.query(Info).filter(Info.UserId == user_id).first()
    if db_information:
        db_information.FirstName = information.first_name
        db_information.LastName = information.last_name
        db_information.FullName = information.first_name + " " + information.last_name
        db_information.DateOfBirth = information.date_of_birth
        db_information.Gender = information.gender
        db_information.Address = information.address
        db.commit()
        db.refresh(db_information)
    return db_information

def get_information_by_user_id(db: Session, user_id: int):
    db_information = db.query(Info).filter(Info.UserId == user_id).first()
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if db_information is None or db_user is None:
        return None
    
    res_info = ResponseInformation(
        id=db_information.id,
        first_name=db_information.FirstName,
        last_name=db_information.LastName,
        full_name=db_information.FullName,
        date_of_birth=db_information.DateOfBirth,
        gender=db_information.Gender,
        address=db_information.Address,
        user_id=db_information.UserId,
        email=db_user.Email,
        password=db_user.Password
    )
    return res_info