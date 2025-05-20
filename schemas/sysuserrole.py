from pydantic import BaseModel

class SysUserRoleBase(BaseModel):
    user_id: int  # Đúng
    role_id: int  # Đúng
    
  