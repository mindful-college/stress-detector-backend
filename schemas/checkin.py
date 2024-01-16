from typing import Optional, Union
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated

PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class CheckinSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    date: datetime = Field(...)
    study_hours: Union[float, None] = Field(...)
    work_hours: Union[float, None] = Field(...)
    step_count: Union[float, None] = Field(...)
    sleep_hours: Union[float, None] = Field(...)
    heart_rate: Union[float, None] = Field(...)
    social_media_usage: Union[float, None] = Field(...)
    stress_level: int = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "date": "2024-01-05 07:30:56",
                "study_hours": 1.5,
                "work_hours": None,
                "step_count" : 10000,
                "sleep_hours" : 8,
                "heart_rate" : 180,
                "social_media_usage" : 3,
                "stress_level": 1,
            }
        }
