from fastapi.openapi.models import Contact
from pydantic import BaseModel
from typing import Optional, List

class AddServer(BaseModel):
    name: str
    host: str
    protocol: str
    port: int
    expected_status: str
    retry_count: int
    alert_interval: int
    is_active: bool = True
    contacts: List[str]
    description: str


class UpdateServer(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    protocol: Optional[str] = None
    port: Optional[int] = None
    expected_status: Optional[str] = None
    retry_count: Optional[int] = None
    alert_interval: Optional[int] = None
    is_active: Optional[bool] = None
    contacts: Optional[List[str]] = None
    description: Optional[str] = None



class RegisterUser(BaseModel):
    username: str
    email: str
    password: str
    name: str
    surname: str

class UpdateUser(BaseModel):
    username: str
    email: str
    password: str
    name: str
    surname: str


class AddContact(BaseModel):
    email: str
    phone: str
    name: str
    surname: str
    is_active: bool = True


class UpdateContact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    is_active: Optional[bool] = None
