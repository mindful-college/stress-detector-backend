from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated


PyObjectId = Annotated[str, Field(alias="_id", default=None)]

class SettingSchema(BaseModel):
    id: Optional[PyObjectId] 
    email: EmailStr = Field(...)
    step_count: bool = Field(...)
    sleep_hours: bool = Field(...)
    heart_rate: bool = Field(...)
    social_media_usage: bool = Field(...)
    notification: bool = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "step_count": False,
                "sleep_hours": True,
                "heart_rate": False,
                "notification": True,
            }
        }
