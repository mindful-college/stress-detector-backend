from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext

from dotenv import load_dotenv
import os
from fastapi import APIRouter, Request
from schemas import user
from database import db
from fastapi_jwt_auth import AuthJWT
import redis

load_dotenv()
router = APIRouter()

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


redis_client = redis.Redis(
  host=REDIS_HOST,
  port=REDIS_PORT,
  password=REDIS_PASSWORD)

redis_client.set('example_key', 'example_value')
value = redis_client.get('example_key')
print(f'The value for "example_key" is: {value.decode("utf-8")}')

class Token(BaseModel):
    access_token: str
    token_type: str

class SingInUser(BaseModel):
    email: str
    name: str

class SingUpUser(BaseModel):
    email: str
    name: str
    password: str
    password_check: str
    uuid: str
    

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
user_collection = db.get_collection("user")
setting_collection = db.get_collection("setting")

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str) -> user.UserSchema | None:
    user = user_collection.find_one({"email" : email})
    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> SingInUser:
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

    except JWTError:
        raise credentials_exception
    user = user_collection.find_one({"email" : email})

    if user is None or user["disabled"] is True:
        raise credentials_exception
    return user

@router.post("/token", response_model=Token, tags=["users"])
@router.post("/v1/signin", response_model=Token, tags=["users"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    if redis_client.get(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/v1/users/me", response_model=SingInUser, tags=["users"])
def read_users_me(
    current_user: Annotated[SingInUser, Depends(get_current_user)]
):
    return {
        "email": current_user["email"],
        "name": current_user["name"],
    }

@router.post("/v1/signup", status_code=status.HTTP_201_CREATED, tags=["users"])
async def sign_up(
    request : Request
):
    sign_up_user: SingUpUser = await request.json()

    if len(sign_up_user["password"]) < 8 or sign_up_user["password"] != sign_up_user["password_check"] or sign_up_user["uuid"] == "":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid user information",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email_count = user_collection.count_documents({"email" : sign_up_user["email"]})
    if email_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email address is already in use",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    uuid_count = user_collection.count_documents({"uuid" : sign_up_user["uuid"]})
    
    if uuid_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You can make upto 3 accounts with one device",
            headers={"WWW-Authenticate": "Bearer"},
        )
     
    processed_user = {
        "email" : sign_up_user["email"],
        "password": get_password_hash(sign_up_user["password"]),
        "name" : sign_up_user["name"],
        "uuid" : sign_up_user["uuid"],
        "disabled" : False,
        "is_first_login" : True,
    }
    user_collection.insert_one(processed_user)

    default_setting = {
        "email": sign_up_user["email"],
        "step_count": False,
        "sleep_hours": False,
        "heart_rate": False,
        "notification": False,
        "notification1": {
            "isOn" : False,
            "hours" : 0,
            "minutes" : 0,
        },
        "notification2": {
            "isOn" : False,
            "hours" : 0,
            "minutes" : 0,
        },
        "notification3": {
            "isOn" : False,
            "hours" : 0,
            "minutes" : 0,
        },
    }
    setting_collection.insert_one(default_setting)


@router.post("/v1/signout", tags=["users"])
def expire_token(Authorize: AuthJWT = Depends()):
    # Todo : Redis
    print("signout")
