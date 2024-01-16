from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from dotenv import load_dotenv
import os
from fastapi import APIRouter
from database import db, redis_client


load_dotenv()
router = APIRouter()

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_collection = db.get_collection("user")


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_key = 'jwt_blacklist_' + token
    is_token_in_blacklist = redis_client.get(token_key)
    if is_token_in_blacklist:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_collection.find_one({"email" : email})
    if user is None or user["disabled"] is True:
        raise credentials_exception
    
    return email

        