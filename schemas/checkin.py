from typing import Optional, Union
from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class CheckinSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    date: date = Field(...)
    study_hours: Union[float, None] = Field(...)
    work_hours: Union[float, None] = Field(...)
    text: Union[str, None] = Field(...)
    voice: Union[str, None] = Field(...) #aws path
    stress_level: int = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "date": "",
                "study_hours": 1.5,
                "work_hours": None,
                "text": "I feel good",
                "voice": "aws path",
                "stress_level": 1,
            }
        }
