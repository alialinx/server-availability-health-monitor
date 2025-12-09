from contextlib import nullcontext
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, requests, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import schemas, status
from app.database.database import get_db
from app.functions.functions import verify_password, system_log, hash_password, is_valid_email, get_request_info
from app.functions.token import get_active_or_new_token
from app.schemas.schema import RegisterUser

router = APIRouter(tags=["Auth"])



@router.post("/register", summary="register")
def register(info:RegisterUser, db=Depends(get_db),req_info=Depends(get_request_info)):


    exists = db.users.find_one({"username": info.username})

    if exists:
        raise HTTPException(status_code=400, detail="Username already registered")

    if not is_valid_email(info.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    payload = {
        "username": info.username,
        "email": info.email,
        "name": info.name,
        "surname": info.surname,
        "password_hash":hash_password(info.password),
        "is_admin":False,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "updated_at": None,
        "last_login_at": None,
        "register_ip": req_info["ip"],
    }



    result = db.users.insert_one(payload)
    user_id = result.inserted_id
    system_log(db=db,log_type="register", user_id=user_id, payload={"ip": req_info["ip"], "user_agent":req_info["user_agent"]})


    return {"succes":True,"message": "Registration successful", "user_id":str(user_id)}




@router.post("/login",summary="Login user")
def login(form_data: OAuth2PasswordRequestForm = Depends(),db=Depends(get_db),req_info=Depends(get_request_info)):

    username = form_data.username
    password = form_data.password

    user = db.users.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not found")


    hashed_password = user.get("password_hash")
    if not verify_password(password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect password or username")


    token, expires_at= get_active_or_new_token(user, db)

    system_log(db=db,log_type="login", user_id=user["_id"], payload={"ip": req_info["ip"], "user_agent":req_info["user_agent"]})

    db.users.update_one({"_id": user["_id"]}, {"$set":{"last_login_at":  datetime.now().strftime("%d.%m.%Y %H:%M:%S"),"token_expires_at": expires_at.timestamp() }})


    return {"success": True, "message":"login successful" , "access_token": token, "token_type": "bearer", "expires_at":expires_at.isoformat()}


@router.get("/logout",summary="Logout user")
def logout():
    return {"success": True, "message": "Logout successful "}





