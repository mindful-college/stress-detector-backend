from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class ContactUsSchema(BaseModel):
    email: EmailStr= Field(...)
    support_type: str = Field(...)
    message: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user5@example.com",
                "support_type": "question",
                "message": "Hi, I have been using this app for 2 years, and I have a quick question about..."
            }
        }