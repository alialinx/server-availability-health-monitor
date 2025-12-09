from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database.database import get_db
from app.functions.functions import system_log, get_request_info
from app.functions.token import get_current_user
from app.schemas.schema import AddServer, UpdateServer

router = APIRouter(tags=["Servers"])


@router.get("/servers/{server_id}",  summary= "Get server")
def get_server(server_id: str, db= Depends(get_db),current = Depends(get_current_user),req_info=Depends(get_request_info)):

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    try:
        server_oid = ObjectId(server_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid server_id")

    user_id = current["user"]["_id"]

    result = db.servers.find_one({"_id": server_oid, "user_id": user_id})

    if not result:
        raise HTTPException(status_code=404, detail="Server not found")

    result["_id"] = str(result["_id"])

    system_log(db=db,log_type="get_server",user_id=user_id,  payload={"ip": req_info["ip"], "user_agent":req_info["user_agent"], "data":result} )

    return {"success": True,"message":"get data success","data": result}


@router.get("/servers", summary= "Get all servers")
def get_all_servers(db= Depends(get_db),current=Depends(get_current_user), req_info=Depends(get_request_info)):

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    user_id = current["user"]["_id"]

    servers = list(db.servers.find({"user_id": user_id}))

    if not servers:
        return {"success": True, "message": "servers not found", "data": []}

    system_log(db=db, log_type="get_all_server", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"], "data": servers})

    for s in servers:
        s["_id"] = str(s["_id"])

    return {"success": True, "message": "get all data success", "data": servers}


@router.post("/servers", summary="Add Server")
def add_server(info: AddServer, db=Depends(get_db),current = Depends(get_current_user),req_info=Depends(get_request_info)):

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    user_id = current["user"]["_id"]

    exists = db.servers.find_one({"host": info.host, "user_id": user_id})

    if exists:
        raise HTTPException(status_code=400, detail="Server already exists")


    contacts_emails = []



    for contact_id in info.contacts:
        contact =  db.contacts.find_one({"_id":ObjectId(contact_id), "user_id": user_id })

        if contact:
            contacts_emails.append(contact["email"])


    payload = {
        "name": info.name,
        "host": info.host,
        "protocol": info.protocol,
        "port": info.port,
        "user_id": user_id,
        "expected_status": info.expected_status,
        "retry_count": info.retry_count,
        "alert_interval":info.alert_interval,
        "description": info.description,
        "contacts": contacts_emails,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "is_active": info.is_active,
        "last_status": None,
        "last_checked_at": None,
        "last_alert_at": None,

    }

    result = db.servers.insert_one(payload)
    insert_id = str(result.inserted_id)

    system_log(db=db,log_type="add_server", user_id=user_id, payload={"ip": req_info["ip"], "user_agent":req_info["user_agent"], "data":payload, "insert_id": insert_id})

    return {"success":True,"message": "Server Added","insert_id": insert_id}


@router.put("/servers/{server_id}", summary= "Update server")
def update_server(server_id:str, payload:UpdateServer , db = Depends(get_db), current = Depends(get_current_user), req_info=Depends(get_request_info)):

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    try:
        server_oid = ObjectId(server_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid server_id")

    user_id = current["user"]["_id"]

    result = db.servers.find_one({"_id": server_oid, "user_id": user_id})
    if not result:
        raise HTTPException(status_code=404, detail="Server not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "contacts" in update_data:
        contacts_emails = []
        for contact_id in update_data["contacts"]:
            contact = db.contacts.find_one({"_id": ObjectId(contact_id), "user_id": user_id})
            if contact:
                contacts_emails.append(contact.get("email"))
        update_data["contacts"] = contacts_emails

    if "host" in update_data:
        exists = db.servers.find_one({"host": update_data["host"], "user_id": user_id, "_id":{"$ne":server_oid}})

        if exists:
            raise HTTPException(status_code=400, detail="Server already exists")

    update_data = {k: v for k, v in update_data.items() if v not in ("", None)}
    update_data["updated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    db.servers.update_one({"_id": server_oid, "user_id": user_id},{"$set": update_data})

    system_log(db=db, log_type="update_server", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"],    "data": payload.model_dump(), "server_oid": server_oid})

    return {"success": True, "message": "Server Updated", "data": update_data}



@router.delete("/servers/{server_id}", summary= "Delete server")
def delete_server(server_id:str, db = Depends(get_db), current = Depends(get_current_user), req_info=Depends(get_request_info)):

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    try:
        server_oid = ObjectId(server_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid server_id")

    user_id = current["user"]["_id"]

    result = db.servers.find_one({"_id": server_oid, "user_id": user_id})
    if not result:
        raise HTTPException(status_code=404, detail="Server not found")

    db.servers.delete_one({"_id": server_oid, "user_id": user_id})

    system_log(db=db, log_type="delete_server", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"], "server_oid": server_oid})

    return {"success": True, "message": "Server Deleted"}