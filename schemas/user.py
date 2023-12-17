from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class UserSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    name: str = Field(...)
    password: str = Field(...)
    uuid: str = Field(...)
    disabled: bool = Field(...)
    is_first_login: bool = Field(...)
    points: int = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "name": "jiji",
                "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "uuid": "jiji-uuid",
                "disabled": False,
                "is_first_login": True,
                "points": 0,
            }
        }
