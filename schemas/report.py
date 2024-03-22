from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class ReportSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    date: datetime = Field(...)
    self_stress_level: int = Field(...)
    chat: list[str] = Field(...)
    summary: object = Field(...)
    stress_level: int = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "date": "2024-01-05 07:30:56",
                "chat" : ["chat1", "chat2"],
                "self_stress_level": 1.5,
                "summary": {
                    "text" : ["happy", "good"],
                    "voice" : ["high tone", "relaxed voice"]
                },
                "stress_level": 1,
            }
        }
