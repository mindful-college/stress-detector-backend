from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from database import db, redis_client

router = APIRouter(tags=["items"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_collection = db.get_collection("user")
setting_collection = db.get_collection("setting")

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))

@router.put("/settings/permissions")
async def test(token: Annotated[str, Depends(oauth2_scheme)], permission_type: str, permission: bool):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if permission_type is None or permission is None:
        raise credentials_exception

    result = setting_collection.update_one({"email" : email},{"$set":{permission_type:permission}})

    new_result = setting_collection.find_one({"email" : email})

    return {"stepCounts": new_result["step_count"], "sleepHours":new_result["sleep_hours"],
        "heartRate": new_result["heart_rate"], "socialMediaUsage": new_result["social_media_usage"], "notification":new_result["notification"]}

@router.get("/settings/permissions")
async def test(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    result = setting_collection.find_one({"email" : email})

    return {"stepCounts": result["step_count"], "sleepHours":result["sleep_hours"],
        "heartRate": result["heart_rate"], "socialMediaUsage": result["social_media_usage"], "notification":result["notification"]}