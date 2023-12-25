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

    return {permission_type: permission}

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
    print(result)
    return {"Step Count": result["step_count"],"Heart Rate": result["heart_rate"], 
        "Sleep Hours":result["sleep_hours"], "Notification":result["notification"]}