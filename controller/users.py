from sqlalchemy.orm import Session
from models.models import SysUser
from schemas.users import UserAuth
from controller.sysuserrole import create_sysuserrole

def create_user(db: Session, user: UserAuth):
    db_user = SysUser(
        Email=user.email,
        Password=user.password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # create instance sys_user_role
    db_sysUserRole = create_sysuserrole(db, db_user.id)
    db.add(db_sysUserRole)
    db.refresh(db_sysUserRole)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(SysUser).filter(SysUser.id == user_id).first()

def authenticate_user(db: Session, user: UserAuth):
    db_user = db.query(SysUser).filter(SysUser.Email == user.email).first()
    if db_user is None or db_user.Password != user.password:
        return None
    return db_user