# Server Monitoring & Email Alert System

This project is a personal learning project to practice **FastAPI**, **PyMongo**, **JWT authentication**, and **background server monitoring**.  
The system checks servers in the background and sends email alerts when a server is down or gives an unexpected response.

---

## 🧩 Overview

This project has two parts:

### 1. FastAPI Backend
- User authentication (JWT)
- Server management (CRUD)
- Contact management
- Swagger API documentation
- Stores all data in MongoDB

### 2. Monitoring Worker
- Runs in the background
- Checks servers at set intervals
- Sends email alerts
- Saves results to MongoDB

Both parts work together to create a simple monitoring system.

---

## 🚀 Features

### 🖥 Server Monitoring
- Supports HTTP, HTTPS, and ICMP (ping)
- Each server has custom settings:
  - Check interval (seconds)
  - Timeout
  - Expected status code
  - Active / inactive
- Stores:
  - Last check time
  - Last status
  - Failure count

---

### 📩 Email Alerts
- Sends alert when a server fails for the first time
- Sends another alert if the problem continues after 1 hour
- Uses SMTP settings from `.env`
- Supports multiple contacts per user

---

### 👤 Contact Management
- Add a contact  
- Update a contact  
- Delete a contact  
- List all contacts  

Each contact belongs to the user.

---

### 🔐 Authentication
- JWT login system  
- Passwords hashed using `sha256_crypt`  
- Token expiration  
- Protected Swagger UI  

---

# ⚙️ Installation Guide

This section explains how to install and run the project.

---

## 1️⃣ Install Requirements

pip install -r requirements.txt

You do not need to use a virtual environment or Docker.  
The project runs directly with Python.

---

## 2️⃣ Create a `.env` File

The project requires a `.env` file containing MongoDB, JWT, and SMTP settings.

Create a `.env` file in the project root and paste the template below:

```env
MONGO_HOST=
MONGO_PORT=
MONGO_DB_NAME=
MONGO_DB_USER=
MONGO_DB_PASS=
MONGO_AUTH_SOURCE=

SECRET_KEY=
ALGORITHM=
TOKEN_EXPIRE_MINUTES=

SWAGGER_USER=
SWAGGER_PASS=

SMTP_HOST=
SMTP_PORT=
SMTP_EMAIL=
SMTP_PASSWORD=
SENDER_NAME=

### 🔒 Why is the `.env` file important?
- It keeps your sensitive information safe  
- It allows you to change settings without touching the code  
- You should **never upload this file to GitHub**

---

````

## 3️⃣ Start the FastAPI Server

Run the API using Uvicorn:

uvicorn app.main:app --reload

Open the API documentation:

http://localhost:8000/docs

You can log in, test endpoints, and view examples directly from Swagger UI.

---

## 4️⃣ Start the Monitoring Worker

The worker checks servers and sends email alerts.  
You must run it separately from the FastAPI server.

Start the worker:

python worker/monitor.py

Now your system is fully active:

- FastAPI API → manages users, servers, contacts  
- Worker → checks server status and sends email alerts  

---

# 🧪 How to Use the System

### 1. Login and get a JWT token  
Use this token for all protected API endpoints.

### 2. Create your contacts  
These people will receive the alert emails.

### 3. Add a server to monitor  
Set:
- URL  
- Check interval  
- Timeout  
- Expected status code  
- Enable monitoring  

### 4. Worker checks the server  
The worker updates:
- last check time  
- last status  
- fail count  

### 5. Email is sent on failure  
If the failure continues:
- A new alert is sent every 1 hour

---

# 🧹 Extra Notes

- No virtual environment required  
- No Docker required  
- Runs on Windows, macOS, and Linux  
- You can deploy the project easily on any server  
- Do not share your `.env` file

---

# 🎯 Summary

This project gives you:

✔ FastAPI REST API  
✔ MongoDB storage  
✔ JWT authentication  
✔ Contact and server management  
✔ Background worker  
✔ Email alert system  
✔ Clean project structure  
✔ Easy environment configuration  

