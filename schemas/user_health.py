from typing import Optional, Union
from datetime import date
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class UserHealthSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    date: date = Field(...)
    step_count: Union[float, None] = Field(...)
    sleep_hours: Union[float, None] = Field(...)
    heart_rate: Union[float, None] = Field(...)
    social_media_usage: Union[float, None] = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "date": "",
                "step_count": 1.5,
                "sleep_hours": None,
                "heart_rate": 85,
                "social_media_usage": 2,
            }
        }
