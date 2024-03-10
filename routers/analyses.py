from datetime import datetime,timedelta
from typing import Annotated, Union, List
from fastapi import Depends, FastAPI, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from schemas import checkin
from common.token import verify_token
from database import db

app = FastAPI()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
checkin_collection = db.get_collection("checkin")
report_collection = db.get_collection("report")

@router.get("/analyses/data/weekly")
async def get_checkin_data(token: Annotated[str, Depends(oauth2_scheme)]):
    email = verify_token(token)
    dt = datetime.now()
    count = 0
    result = checkin_collection.find({"email" : email},{'_id':False}).sort('date')
    checkin_list = list()
    for data in result:
        data['day'] = data['date'].weekday()
        if(len(checkin_list)<1):
            checkin_list.append(data)
        else:
            dday = (data['date']-dt).days
            if(dday == 0):
                checkin_list[-1]['study_hours'] = ( checkin_list[-1]['study_hours'] * count + data['study_hours'] ) / ( count + 1 )
                checkin_list[-1]['work_hours'] = ( checkin_list[-1]['work_hours'] * count + data['work_hours'] ) / ( count + 1 )
                checkin_list[-1]['step_count'] = ( checkin_list[-1]['step_count'] * count + data['step_count'] ) / ( count + 1 )
                checkin_list[-1]['sleep_hours'] = ( checkin_list[-1]['sleep_hours'] * count + data['sleep_hours'] ) / ( count + 1 )
                checkin_list[-1]['heart_rate'] = ( checkin_list[-1]['heart_rate'] * count + data['heart_rate'] ) / ( count + 1 )
                checkin_list[-1]['social_media_usage'] = ( checkin_list[-1]['social_media_usage'] * count + data['social_media_usage'] ) / ( count + 1 )
                checkin_list[-1]['stress_level'] = ( checkin_list[-1]['stress_level'] * count + data['stress_level'] ) / ( count + 1 )

            else:
                for count_day in range(1,dday):
                    no_data = {
                        'email': 'Test123@test.com', 
                        'date': dt + timedelta(days=count_day), 
                        'study_hours': 0, 
                        'work_hours': 0, 
                        'step_count': None, 
                        'sleep_hours': 0, 
                        'heart_rate': 0, 
                        'social_media_usage': 0, 
                        'stress_level': 0
                    }
                    no_data['day'] = no_data['date'].weekday()
                    checkin_list.append(no_data)
                count = 0
                checkin_list.append(data)
        count = count + 1
        dt = data['date']

    date = list()
    study_hours = list()
    work_hours = list()
    step_count = list()
    sleep_hours = list()
    heart_rate = list()
    social_media_usage = list()
    stress_level = list()
    days = list()

    for data in checkin_list:
        date.append(data['date'])
        study_hours.append(data['study_hours'])
        work_hours.append(data['work_hours'])
        step_count.append(data['step_count'])
        sleep_hours.append(data['sleep_hours'])
        heart_rate.append(data['heart_rate'])
        social_media_usage.append(data['social_media_usage'])
        stress_level.append(data['stress_level'])
        days.append(data['day'])
    # print(checkin_list)
    return {'study_hours': study_hours, 'date': date, 'work_hours':work_hours, 'sleep_hours':sleep_hours, 'heart_rate':heart_rate, 'social_media_usage':social_media_usage,
            'stress_level': stress_level, 'step_count':step_count,'days':days}



@router.get("/analyses/data/monthly")
async def get_checkin_data(token: Annotated[str, Depends(oauth2_scheme)]):
    email = verify_token(token)
    pipeline = [
        {
        "$project": {
            "email": 1,
            "month": {"$month": "$date"},
            "year": {"$year": "$date"},
            "study_hours": 1,
            "work_hours": 1,
            "sleep_hours": 1,
            "social_media_usage": 1,
            "stress_level": 1,
            "step_count": 1,
            "heart_rate": 1
        }
    },
    {
        "$group": {
            "_id": {
                "email": "$email",
                "year": "$year",
                "month": "$month"
            },
            "average_study_hours": {"$avg": "$study_hours"},
            "average_work_hours": {"$avg": "$work_hours"},
            "average_sleep_hours": {"$avg": "$sleep_hours"},
            "average_social_media_usage": {"$avg": "$social_media_usage"},
            "average_stress_level": {"$avg": "$stress_level"},
            "average_step_count": {"$avg": "$step_count"},
            "average_heart_rate": {"$avg": "$heart_rate"}
        }
    },
    {
        "$sort": {
            "_id.year": 1,
            "_id.month": 1
        }
    }
    ]
    results = checkin_collection.aggregate(pipeline)
    checkin_list = list(results)
    print(checkin_list)
    years = list()
    months = list()
    study_hours = list()
    work_hours = list()
    sleep_hours = list()
    social_media_usage = list()
    stress_level = list()
    step_count = list()
    heart_rate = list()
    year = -1
    month = -1
    for data in checkin_list:
        if(year<0):
            year = data['_id']['year']
            month = data['_id']['month']
        while year != data['_id']['year'] or month != data['_id']['month']:
            years.append(year)
            months.append(month)
            study_hours.append(0)
            work_hours.append(0)
            sleep_hours.append(0)
            social_media_usage.append(0)
            stress_level.append(0)
            step_count.append(0)
            heart_rate.append(0)
            year = year + ( month // 12 )
            month = ( month % 12 ) + 1
            

        years.append(year)
        months.append(month)
        study_hours.append(data['average_study_hours'])
        work_hours.append(data['average_work_hours'])
        sleep_hours.append(data['average_sleep_hours'])
        social_media_usage.append(data['average_social_media_usage'])
        stress_level.append(data['average_stress_level'])
        step_count.append(data['average_step_count'])
        heart_rate.append(data['average_heart_rate'])
        year = year + ( month // 12 )
        month = ( month % 12 ) + 1

            
    return {'study_hours': study_hours, 'work_hours':work_hours, 'sleep_hours':sleep_hours, 'heart_rate':heart_rate, 'social_media_usage':social_media_usage,
            'stress_level': stress_level, 'step_count':step_count, 'years': years, 'months': months}