from datetime import datetime
from typing import Annotated, Union
from fastapi import Depends, FastAPI, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from schemas import checkin
from common.token import verify_token
from database import db
from openai import OpenAI
import os
import json

OPEN_AI_KEY = os.getenv("OPEN_AI")
app = FastAPI()
router = APIRouter()
client = OpenAI(api_key=OPEN_AI_KEY)

class ChatData(BaseModel):
    text: Union[list[str], None]
    stress_level: int

class CheckInData(BaseModel):
    study_hours: Union[float, None]
    work_hours: Union[float, None]
    voice: Union[list[bytes], None]
    step_count: Union[float, None]
    sleep_hours: Union[float, None]
    heart_rate: Union[float, None]
    social_media_usage: Union[float, None]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
checkin_collection = db.get_collection("checkin")
report_collection = db.get_collection("report")
user_collection = db.get_collection("user")

openai_input_text = '''
    You are here to predict stress levels based on a few sentences. I will provide you with the sentences and a self-reported stress level (1 to 5, inclusive integer) as input. I want you to give me the predicted stress level (1 to 5, inclusive double) and 2 to 5 most impactful keywords for predictions in order of importance.

    The stress levels are defined as follows: 1: 'Very Low', 2: 'Low', 3: 'Moderate', 4: 'High', 5: 'Very High'. Please provide the output in the same format as the input.

    Here is a sample input:
    {
    text: "My day has been going well. I walked my dog this morning and watched a few K-dramas. Nothing too special, but it is relaxing. I am planning to have dinner with my family this evening.",
    stress-level: 3
    }

    Here is the output:
    {
    text: ["well", "relaxing", "dinner with family"],
    stress-level: 3.5
    }

    Please say yes if you understand this
'''

@router.post("/v1/report", tags=["checkin"])
async def insert_checkin(token: Annotated[str, Depends(oauth2_scheme)], request: Request):
    user_input: CheckInData = await request.json()
    email = verify_token(token)
    
    if email:
        today = datetime.today().replace(microsecond=0)
        user_text = '''
        {
            "text": "%s",
            "stress-level": %d
        }
        ''' % (user_input["text"], user_input["stress_level"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": openai_input_text},
                {"role": "assistant", "content": "Yes"},
                {"role": "user", "content": user_text}
            ]
        )
        message = response.choices[0].message.content
        parsed_dict = json.loads(message)
        report_data = {
            "email": email,
            "date": today,
            "chat": user_input["text"],
            "summary": {
                "text" : parsed_dict["text"]
            },
            "self_stress_level": user_input["stress_level"],
            "stress_level": parsed_dict["stress-level"]
        }
        report_collection.insert_one(report_data)
        user = user_collection.find_one({"email" : email})
        user_collection.update_one({"email" : email},{"$set":{"points": user["points"] + 100}})

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
        }
        checkin_collection.insert_one(checkin_data)
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
        
