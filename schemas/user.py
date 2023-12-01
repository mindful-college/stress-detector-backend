from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr = Field(...)
    name: str = Field(...)
    password: str = Field(...)
    uuid: str = Field(...)
    disabled: bool = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "name": "jiji",
                "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "uuid": "jiji-uuid",
                "disabled": False
            }
        }
