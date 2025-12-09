from datetime import datetime
from http.client import HTTPException

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends

from app.database.database import get_db
from app.functions.functions import get_request_info, system_log
from app.functions.token import get_current_user
from app.schemas.schema import AddContact, UpdateContact

router = APIRouter(tags=["Contacts"])



@router.get("/contacts/{id}", summary="Get Contact Details")
def get_contact(contact_id: str, db= Depends(get_db), current= Depends(get_current_user), req_info=Depends(get_request_info)):


    user_id = current["user"]["_id"]

    try:
        contact_oid = ObjectId(contact_id)
    except Exception:
        return {"success": False, "message": "Invalid Contact ID"}


    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    result = db.contacts.find_one({"_id": contact_oid, "user_id":user_id})

    if not result:
        return {"success": False, "message": "Contact not found"}

    result["_id"] = str(result["_id"])

    system_log(db=db, log_type="get_contact", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"], "data": result})

    return {"success": True, "message":"get data success","data": result}

@router.get("/contacts", summary="Get All Contacts")
def get_all_contacts(db= Depends(get_db), current= Depends(get_current_user), req_info=Depends(get_request_info)):

    user_id = current["user"]["_id"]

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    result = db.contacts.find({"user_id":user_id})

    result_list = list(result)

    if not result_list:
        return {"success": False, "message": "Contacts not found"}

    for s in result_list:
        s["_id"] = str(s["_id"])

    system_log(db=db, log_type="get_all_contact", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"], "data": result_list})

    return {"success": True, "message":"get all data success","data": result_list}

@router.post("/contacts", summary="Add Contact")
def add_contact(payload:AddContact, db = Depends(get_db), current= Depends(get_current_user), req_info=Depends(get_request_info)):

    user_id = current["user"]["_id"]

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    exists = db.contacts.find_one({"user_id":user_id, "email":payload.email})

    if exists:
        return {"success": False, "message": "Contact already exists"}

    new_contact = {
        "email": payload.email,
        "name": payload.name,
        "surname": payload.surname,
        "phone": payload.phone,
        "user_id": user_id,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "is_active": payload.is_active,
    }

    result = db.contacts.insert_one(new_contact)

    insert_id = str(result.inserted_id)

    if not insert_id :
        return {"success": False, "message": "Contact insert failed"}


    system_log(db=db,log_type="add_contact", user_id=user_id, payload={"ip": req_info["ip"], "user_agent":req_info["user_agent"], "data":new_contact, "insert_id": insert_id})

    return {"success":True,"message": "Contact Added","insert_id": insert_id}

@router.put("/contacts/{id}", summary="Update Contact")
def update_contact(contact_id:str,payload:UpdateContact, db = Depends(get_db), current= Depends(get_current_user), req_info=Depends(get_request_info) ):

    user_id = current["user"]["_id"]

    try:
        contact_oid = ObjectId(contact_id)
    except Exception:
        return {"success": False, "message": "Invalid Contact ID"}

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    check_data = db.contacts.find_one({"user_id":user_id, "_id":contact_oid})

    if not check_data:
        return {"success": False, "message": "Contact not found"}


    update_data = payload.model_dump(exclude_unset=True)


    if "email" in update_data:

        exists = db.contacts.find_one({"user_id":user_id, "email":payload.email, "_id":{"$ne":contact_oid}})
        if exists:
            return {"success": False, "message": "Contact already exists"}

    update_data = {k: v for k, v in update_data.items() if v not in ("", None)}
    update_data["updated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    db.contacts.update_one({"_id": contact_oid, "user_id": user_id},{"$set": update_data})

    system_log(db=db, log_type="update_contact", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"],    "data": payload.model_dump(), "contact_oid": contact_oid})

    return {"success": True, "message": "Contact Updated", "data": update_data}

@router.delete("/contacts/{id}", summary="Delete Contact")
def delete_contact(contact_id:str, db = Depends(get_db),current= Depends(get_current_user), req_info=Depends(get_request_info)):

    user_id = current["user"]["_id"]

    try:
        contact_oid = ObjectId(contact_id)
    except Exception:
        return {"success": False, "message": "Invalid Contact ID"}

    if not current.get("success"):
        return {"success": False, "message": current.get("error", "unauthorized")}

    result = db.contacts.find_one({"_id": contact_oid, "user_id":user_id})

    if not result:
        return {"success": False, "message": "Contact not found"}

    db.contacts.delete_one({"_id": contact_oid, "user_id": user_id})

    system_log(db=db, log_type="delete_contact", user_id=user_id, payload={"ip": req_info["ip"], "user_agent": req_info["user_agent"], "contact_oid": contact_oid})

    return {"success": True, "message": "Contact Deleted"}