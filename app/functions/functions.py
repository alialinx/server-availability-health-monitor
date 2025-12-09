import os
import re

from cryptography import fernet
from passlib.handlers.sha2_crypt import sha256_crypt
import inspect
from datetime import datetime
from fastapi import Request, Depends

def system_log(db,log_type: str,user_id=None,payload: dict = None,error: str = None,):

    stack = inspect.stack()[1]

    caller_info = {"function": stack.function,"file": os.path.basename(stack.filename),"line": stack.lineno}
    log_doc = {"type": log_type,"user_id": str(user_id) if user_id else None,"payload": payload or {},"error": error,"caller": caller_info,"timestamp":datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
    return db.system_logs.insert_one(log_doc)



def verify_password(plain: str, hashed: str) -> bool:
    return sha256_crypt.verify(plain, hashed)


def hash_password(password: str) -> str:
    return sha256_crypt.hash(password)


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def get_request_info(request: Request):
    client_ip = request.client.host if request else "unknown"
    user_agent = request.headers.get("User-Agent") if request else "unknown"
    return {"ip": client_ip, "user_agent": user_agent}


