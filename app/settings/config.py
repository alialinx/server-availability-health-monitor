import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()


MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_DB_USER = os.getenv("MONGO_DB_USER")
MONGO_DB_PASS = os.getenv("MONGO_DB_PASS")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE")

MONGO_URI = (
    f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASS}"
    f"@{MONGO_HOST}:{MONGO_PORT}/"
    f"?authSource={MONGO_AUTH_SOURCE}"
)



TOKEN_URL = "/login"
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES"))



SWAGGER_USER = os.getenv("SWAGGER_USER")
SWAGGER_PASS = os.getenv("SWAGGER_PASS")


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_EMAİL = os.getenv("SMTP_EMAİL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_NAME = os.getenv("SENDER__NAME")