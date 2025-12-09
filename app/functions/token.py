import token
from datetime import datetime, timezone, timedelta
from os.path import exists

import jwt
from bson import ObjectId
from fastapi import Depends
# region Imports
from fastapi.security import OAuth2PasswordBearer

from app.database.database import get_db
from app.settings.config import TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# endregion Imports

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")



def create_access_token(data: dict):

    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "user_id":str(data.get("_id")),
        "role":data.get("role", "user"),
        "exp": int(expire.timestamp())
        }

    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return token,expire


def save_token(token:str,user_id:str,expires_at:datetime,db=Depends(get_db)):

    db.tokens.delete_one({"user_id":user_id})

    data = {
        "user_id":user_id,
        "expires_at":expires_at.timestamp(),
        "token":token,
        "created_at":datetime.now(timezone.utc).isoformat(),
    }

    db.tokens.insert_one(data)
    return {"success":True}


def validate_token(token:str, db=Depends(get_db)):

    result = db.tokens.find_one({"token":token})

    if not result:

        return {"success":False, "error":"token not found"}

    expires_at_ts = result.get("expires_at")
    if not expires_at_ts:
        return {"success": False, "error": "expires_at not found"}

    expires_at = datetime.fromtimestamp(expires_at_ts, timezone.utc)

    now = datetime.now(timezone.utc)
    if expires_at < now:
        return {"success": False, "error": "token expired"}

    return {"success": True, "data": result}




def get_current_user(token: str = Depends(oauth2_scheme),db=Depends(get_db)):



    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"success":False, "error":"token expired"}
    except jwt.PyJWTError:
        return {"success":False, "error":"invalid token"}

    user_id = payload.get("user_id")

    if not user_id:
        return {"success":False, "error":"user_id not found"}

    token_check = validate_token(token,db)

    if not token_check.get("success"):
        return {"success":False, "error":"token not valid"}

    try:
        oid = ObjectId(user_id)
    except:
        return {"success":False, "error":"user_id invalid"}


    user = db.users.find_one({"_id":oid})
    if not user:
        return {"success":False, "error":"user not found"}

    user["_id"] = str(user["_id"])

    return {"success":True, "user":user}



def get_active_or_new_token(user:dict,db=Depends(get_db)):

    user_id = str(user["_id"])
    now = datetime.now(timezone.utc)


    existing = db.tokens.find_one({"user_id": user_id})

    if existing:

        expires_at = datetime.fromtimestamp(existing["expires_at"], timezone.utc)
        token = existing["token"]


        if expires_at > now:
            return token, expires_at

    new_token, expires_at = create_access_token(data=user)
    save_token(new_token,user_id,expires_at,db)

    return new_token,expires_at













