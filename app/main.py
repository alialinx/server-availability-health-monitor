# app/main.py

from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.cors import CORSMiddleware
import secrets
from app.settings.config import SWAGGER_USER, SWAGGER_PASS

from .routers import servers, contacts, auth, users


# ---------------- APP CONFIG ----------------
app = FastAPI(
    title="Server Availability Health Monitor",
    description="An API that monitors server availability and health status.",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
    contact={"name": "Ali A.", "email": "alialinxz@gmail.com"},
)




# ---------------- BASIC AUTH ----------------
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, SWAGGER_USER)
    correct_password = secrets.compare_digest(credentials.password, SWAGGER_PASS)

    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return True


# ---------------- HOME (Swagger giriş ekranı) ----------------
@app.get("/", include_in_schema=False)
async def homepage(request: Request, auth: bool = Depends(verify_credentials)):

    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Server Availability Health Monitor",
    )

    return response


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROUTERS ----------------
app.include_router(servers.router)
app.include_router(contacts.router)
app.include_router(users.router)
app.include_router(auth.router)
