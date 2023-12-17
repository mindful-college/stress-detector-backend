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
    notification: bool = Field(...)
    notification1: object = Field(...)
    notification2: object = Field(...)
    notification3: object = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "jiji@example.com",
                "step_count": False,
                "sleep_hours": False,
                "heart_rate": False,
                "notification": False,
                "notification1": {
                    "isOn" : False,
                    "hours" : 0, # UTC 0~23
                    "minutes" : 0, # 0, 15, 30, 45
                },
                "notification2": {
                    "isOn" : False,
                    "hours" : 8, # UTC 0~23
                    "minutes" : 15, # 0, 15, 30, 45
                },
                "notification3": {
                    "isOn" : True,
                    "hours" : 16, # UTC 0~23
                    "minutes" : 30, # 0, 15, 30, 45
                },
            }
        }
