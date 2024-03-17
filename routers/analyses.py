from datetime import datetime,timedelta
from typing import Annotated, Union, List
from fastapi import Depends, FastAPI, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from schemas import checkin
from common.token import verify_token
from database import db
import numpy as np

app = FastAPI()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
checkin_collection = db.get_collection("checkin")
report_collection = db.get_collection("report")

@router.get("/analyses/data/weekly")
async def get_checkin_data(token: Annotated[str, Depends(oauth2_scheme)]):
    email = verify_token(token)

    pipeline = [
        {
            "$match": {
                "email": email  # Assuming 'email' variable is defined elsewhere
            }
        },
        {
            "$project": {
                "email": 1,
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"},
                        "day": {"$dayOfMonth": "$date"}
                    }
                },
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
                    "date": "$date"
                },
                "study_hours": {"$avg": "$study_hours"},
                "work_hours": {"$avg": "$work_hours"},
                "sleep_hours": {"$avg": "$sleep_hours"},
                "social_media_usage": {"$avg": "$social_media_usage"},
                "stress_level": {"$avg": "$stress_level"},
                "step_count": {"$avg": "$step_count"},
                "heart_rate": {"$avg": "$heart_rate"}
            }
        },
        {
            "$sort": {
                "_id.date": 1
            }
        }
    ]
    results = checkin_collection.aggregate(pipeline)
    dt = datetime.now()
    days_count = 0
    count = 0
    # for data in results:
    #     print(data)
    # print(results)
    result = checkin_collection.find({"email" : email},{'_id':False}).sort('date')
    checkin_list = list()

    
    for data in results:
        data['day'] = data['_id']['date'].weekday()
        if(len(checkin_list)<1):
            data['date'] = data['_id']['date']
            checkin_list.append(data)
            days_count = days_count +1
        else:
            dday = (data['_id']['date']-dt).days
            for count_day in range(1,dday):
                no_data = {
                    'email': 'Test123@test.com',
                    'date': dt + timedelta(days=count_day),
                    'study_hours': 0,
                    'work_hours': 0,
                    'step_count': 0,
                    'sleep_hours': 0,
                    'heart_rate': 0,
                    'social_media_usage': 0,
                    'stress_level': 0
                }
                no_data['day'] = no_data['date'].weekday()
                checkin_list.append(no_data)
            count = 0
            data['date'] = data['_id']['date']
            checkin_list.append(data)
            days_count = days_count +1
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

    study_hours = np.round(study_hours, 2).tolist()
    work_hours = np.round(work_hours, 2).tolist()
    step_count = np.round(step_count, 2).tolist()
    sleep_hours = np.round(sleep_hours, 2).tolist()
    social_media_usage = np.round(social_media_usage, 2).tolist()
    stress_level = np.round(stress_level, 2).tolist()
    heart_rate = np.round(heart_rate, 2).tolist()

    day_list = ["Sun", "Mon", "Tue", "Wen", "Thur", "Fri", "Sat"]
    for i in range(len(days)):
        days[i]= day_list[days[i]]

    new_date = list()
    new_study_hours = list()
    new_work_hours = list()
    new_step_count = list()
    new_sleep_hours = list()
    new_heart_rate = list()
    new_social_media_usage = list()
    new_stress_level = list()
    new_days = list()

    num = len(date)%7
    length = 7

    if len(days)//length == 0 or num != 0:
        new_date.append(date[0:num])
        new_study_hours.append(study_hours[0:num])
        new_work_hours.append(work_hours[0:num])
        new_step_count.append(step_count[0:num])
        new_sleep_hours.append(sleep_hours[0:num])
        new_heart_rate.append(heart_rate[0:num])
        new_social_media_usage.append(social_media_usage[0:num])
        new_stress_level.append(stress_level[0:num])
        new_days.append(days[0:num])
    for i in range(len(date)//7):
        new_date.append(date[num+i*length:num+length+i*length])
        new_study_hours.append(study_hours[num+i*length:num+length+i*length])
        new_work_hours.append(work_hours[num+i*length:num+length+i*length])
        new_step_count.append(step_count[num+i*length:num+length+i*length])
        new_sleep_hours.append(sleep_hours[num+i*length:num+length+i*length])
        new_heart_rate.append(heart_rate[num+i*length:num+length+i*length])
        new_social_media_usage.append(social_media_usage[num+i*length:num+length+i*length])
        new_stress_level.append(stress_level[num+i*length:num+length+i*length])
        new_days.append(days[num+i*length:num+length+i*length])
    return {'study_hours': new_study_hours, 'date': new_date, 'work_hours':new_work_hours, 'sleep_hours':new_sleep_hours, 'heart_rate':new_heart_rate, 'social_media_usage':new_social_media_usage,
            'stress_level': new_stress_level, 'step_count':new_step_count,'days':new_days, 'days_count':days_count}



@router.get("/analyses/data/monthly")
async def get_checkin_data(token: Annotated[str, Depends(oauth2_scheme)]):
    email = verify_token(token)

    pipeline = [
        {
        "$match": {
            "email": email
        }
    },
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


    study_hours = np.round(study_hours, 2).tolist()
    work_hours = np.round(work_hours, 2).tolist()
    step_count = np.round(step_count, 2).tolist()
    sleep_hours = np.round(sleep_hours, 2).tolist()
    social_media_usage = np.round(social_media_usage, 2).tolist()
    stress_level = np.round(stress_level, 2).tolist()
    heart_rate = np.round(heart_rate, 2).tolist()
    month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i in range(len(months)):
        months[i] = month_list[months[i]-1]

    new_years = list()
    new_study_hours = list()
    new_work_hours = list()
    new_step_count = list()
    new_sleep_hours = list()
    new_heart_rate = list()
    new_social_media_usage = list()
    new_stress_level = list()
    new_months = list()

    length = 6
    num = len(years)%length

    if len(years)//length == 0 or num != 0:
        new_years.append(years[0:num])
        new_study_hours.append(study_hours[0:num])
        new_work_hours.append(work_hours[0:num])
        new_step_count.append(step_count[0:num])
        new_sleep_hours.append(sleep_hours[0:num])
        new_heart_rate.append(heart_rate[0:num])
        new_social_media_usage.append(social_media_usage[0:num])
        new_stress_level.append(stress_level[0:num])
        new_months.append(months[0:num])

    for i in range(len(years)//6):
        new_years.append(years[num+i*length:num+length+i*length])
        new_study_hours.append(study_hours[num+i*length:num+length+i*length])
        new_work_hours.append(work_hours[num+i*length:num+length+i*length])
        new_step_count.append(step_count[num+i*length:num+length+i*length])
        new_sleep_hours.append(sleep_hours[num+i*length:num+length+i*length])
        new_heart_rate.append(heart_rate[num+i*length:num+length+i*length])
        new_social_media_usage.append(social_media_usage[num+i*length:num+length+i*length])
        new_stress_level.append(stress_level[num+i*length:num+length+i*length])
        new_months.append(monthss[num+i*length:num+length+i*length])

    return {'study_hours': new_study_hours, 'work_hours':new_work_hours, 'sleep_hours':new_sleep_hours, 'heart_rate':new_heart_rate, 'social_media_usage':new_social_media_usage,
            'stress_level': new_stress_level, 'step_count':new_step_count, 'years': new_years, 'months': new_months, 'month_count': len(checkin_list)}
