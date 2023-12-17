from typing import Optional, Union
from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class ReportSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    date: date = Field(...)
    summary: object = Field(...)
    stress_level: int = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "date": "",
                "summary": {
                    "text" : ["happy", "good"],
                    "voice" : ["high tone", "relaxed voice"]
                },
                "stress_level": 1,
            }
        }
