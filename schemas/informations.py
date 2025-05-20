from pydantic import BaseModel
from datetime import date

class CreateInformation(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    address: str

class UpdateInformation(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    address: str

class ResponseInformation(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date
    gender: str
    address: str
    user_id: int
    email: str
    password: str