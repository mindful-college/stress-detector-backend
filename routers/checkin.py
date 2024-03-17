from datetime import datetime
from typing import Annotated, Union
from fastapi import Depends, FastAPI, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from schemas import checkin
from common.token import verify_token
from database import db

app = FastAPI()
router = APIRouter()

class CheckInData(BaseModel):
    study_hours: Union[float, None]
    work_hours: Union[float, None]
    text: Union[list[str], None]
    voice: Union[list[bytes], None]
    step_count: Union[float, None]
    sleep_hours: Union[float, None]
    heart_rate: Union[float, None]
    social_media_usage: Union[float, None]
    stress_level: int

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
checkin_collection = db.get_collection("checkin")
report_collection = db.get_collection("report")
user_collection = db.get_collection("user")

@router.post("/v1/checkin", tags=["checkin"])
async def insert_checkin(token: Annotated[str, Depends(oauth2_scheme)], request: Request):
    user_input: CheckInData = await request.json()
    email = verify_token(token)
    
    if email:
        today = datetime.today().replace(microsecond=0)
        checkin_data: checkin.CheckinSchema = {
            "email": email,
            "date": today,
            "study_hours": user_input["study_hours"],
            "work_hours": user_input["work_hours"],
            "step_count": user_input["step_count"],
            "sleep_hours": user_input["sleep_hours"],
            "heart_rate": user_input["heart_rate"],
            "social_media_usage": user_input["social_media_usage"],
            "stress_level": user_input["stress_level"]
        }
        checkin_collection.insert_one(checkin_data)

        # api call for ML prediction
        report_data = {
            "email": email,
            "date": today,
            "summary": {
                "text" : ["happy", "good"],
                "voice" : ["high tone", "relaxed voice"]
            },
            "stress_level": user_input["stress_level"],
        }
        report_collection.insert_one(report_data)
        user = user_collection.find_one({"email" : email})
        user_collection.update_one({"email" : email},{"$set":{"points": user["points"] + 100}})

@router.get("/v1/average", tags=["checkin"])
async def get_average(token: Annotated[str, Depends(oauth2_scheme)]):
    email = verify_token(token)
    if email:
        pipeline = [
            {"$match": {"email": "jiji1@test.com"}},
            {"$group": 
                {
                "_id": None, 
                "avg_sleep_hours": { "$avg": "$sleep_hours" },
                "avg_study_hours": { "$avg": "$study_hours" },
                "avg_work_hours": { "$avg": "$work_hours" },
                "avg_step_count": { "$avg": "$step_count" },
                "avg_heart_rate": { "$avg": "$heart_rate" },
                "avg_social_media_usage": { "$avg": "$social_media_usage" }
                }
            }
        ]
        avgResult = list(checkin_collection.aggregate(pipeline))
        print(avgResult)
        if len(avgResult) > 0:
            return {
                "stepCounts" : avgResult[0]["avg_step_count"] or 6000,
                "sleepHours" : avgResult[0]["avg_sleep_hours"] or 8,
                "studyHours" : avgResult[0]["avg_study_hours"] or 5,
                "workHours" : avgResult[0]["avg_work_hours"] or 4,
                "heartRate" : avgResult[0]["avg_heart_rate"] or 80,
                "socialMediaUsage" : avgResult[0]["avg_social_media_usage"] or 3,
            }
        
