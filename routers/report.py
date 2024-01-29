from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
import os
from database import db, redis_client
from datetime import datetime

router = APIRouter(tags=["items"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_collection = db.get_collection("user")
setting_collection = db.get_collection("setting")
contact_us_collection = db.get_collection("contact_us")
report_collection = db.get_collection("report")
checkin_collection = db.get_collection("checkin")

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))



@router.get("/report/stresslvl", status_code=status.HTTP_200_OK, tags=["items"])
async def get_report_data(date_str: str = Query(...), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # example data of input from front-end : 2024-01-24T12:07:52-08:00
    # parsing date_str
    
    try:
        report_date = datetime.fromisoformat(date_str) # create datetime object
        start_of_day = datetime(report_date.year, report_date.month, report_date.day) # set the start_of_day with the day at 00:00:00 AM
        end_of_day = start_of_day + timedelta(days=1) # set the end_of_day with 00:00:00 (+24hours from start_of_day)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")
    
    # get the report from report_collection 
    latest_report = report_collection.find_one(
        {"email": email, "date": {"$gte": start_of_day, "$lt": end_of_day}}, sort=[("date", -1)] # sort the date in Descending Order to get the latest data
    )

    if latest_report:
        report_without_id = {k: v for k, v in latest_report.items() if k != '_id'} # remove ObjectId part from dictionary
        return report_without_id # return data (from email to stress level)
    else:
        return {"message": "There is no data to report"}
    





@router.get("/report/checkin", status_code=status.HTTP_200_OK, tags=["items"])
async def get_checkin_data(date_str: str = Query(...), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # example data of input from front-end : 2024-01-24T12:07:52-08:00
    # parsing date_str
    
    try:
        report_date = datetime.fromisoformat(date_str) # create datetime object
        start_of_day = datetime(report_date.year, report_date.month, report_date.day) # set the start_of_day with the day at 00:00:00 AM
        end_of_day = start_of_day + timedelta(days=1) # set the end_of_day with 00:00:00 (+24hours from start_of_day)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")
    
    # get the report from report_collection 
    latest_report = checkin_collection.find_one(
        {"email": email, "date": {"$gte": start_of_day, "$lt": end_of_day}}, sort=[("date", -1)] # sort the date in Descending Order to get the latest data
    )

    if latest_report:
        report_without_id = {k: v for k, v in latest_report.items() if k != '_id'} # remove ObjectId part from dictionary
        return report_without_id # return data (from email to stress level)
    else:
        return {"message": "There is no data to report"}   