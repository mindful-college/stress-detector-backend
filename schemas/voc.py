from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class VocSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    category: str = Field(...)
    content: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "category": "compliment",
                "content": "helpful",
            }
        }
