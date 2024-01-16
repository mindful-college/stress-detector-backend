from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class ReportSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    date: datetime = Field(...)
    summary: object = Field(...)
    stress_level: int = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "date": "2024-01-05 07:30:56",
                "summary": {
                    "text" : ["happy", "good"],
                    "voice" : ["high tone", "relaxed voice"]
                },
                "stress_level": 1,
            }
        }
