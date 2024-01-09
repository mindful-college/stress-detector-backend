# from datetime import datetime
# from typing import Annotated, Union
# from fastapi import Depends, FastAPI, APIRouter, Request
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel
# from schemas import checkin
# from common.token import verify_token
# from database import db

# app = FastAPI()
# router = APIRouter()

# class CheckInData(BaseModel):
#     study_hours: Union[float, None]
#     work_hours: Union[float, None]
#     text: Union[list[str], None]
#     voice: Union[list[bytes], None]
#     step_count: Union[float, None]
#     sleep_hours: Union[float, None]
#     heart_rate: Union[float, None]
#     social_media_usage: Union[float, None]
#     stress_level: int

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# checkin_collection = db.get_collection("checkin")
# report_collection = db.get_collection("report")

# @router.post("/v1/checkin", tags=["checkin"])
# async def insert_checkin(token: Annotated[str, Depends(oauth2_scheme)], request: Request):
#     user_input: CheckInData = await request.json()
#     email = verify_token(token)
    
#     if email:
#         today = datetime.today().replace(microsecond=0)
#         checkin_data: checkin.CheckinSchema = {
#             "email": email,
#             "date": today,
#             "study_hours": user_input["study_hours"],
#             "work_hours": user_input["work_hours"],
#             "step_count": user_input["step_count"],
#             "sleep_hours": user_input["sleep_hours"],
#             "heart_rate": user_input["heart_rate"],
#             "social_media_usage": user_input["social_media_usage"],
#             "stress_level": user_input["stress_level"]
#         }
#         checkin_collection.insert_one(checkin_data)

#         # api call for ML prediction
#         report_data = {
#             "email": email,
#             "date": today,
#             "summary": {
#                 "text" : ["happy", "good"],
#                 "voice" : ["high tone", "relaxed voice"]
#             },
#             "stress_level": user_input["stress_level"],
#         }
#         report_collection.insert_one(report_data)
        
    

