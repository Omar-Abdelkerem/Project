import uuid
import time
import random
import string
from . import csv_store

# --- Users ---

def create_user(user_data: dict) -> dict:
    """Creates a new user in users.csv."""
    if 'userid' not in user_data:
        user_data['userid'] = str(uuid.uuid4())
    return csv_store.insert_row('users', user_data)

def get_user_by_email(email: str) -> dict | None:
    """Finds a user by email."""
    users = csv_store.filter_rows('users', email=email)
    return users[0] if users else None

def get_user_by_id(userid: str) -> dict | None:
    """Finds a user by userid."""
    return csv_store.find_by_id('users', 'userid', userid)


# --- Applications ---

def create_application(userid: str, type: str, subtype: str, status: str) -> dict:
    """Creates a new application."""
    apps = csv_store.read_all('applications')
    next_id = csv_store._get_next_id(apps, 'appid')
    
    tracking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    app_data = {
        'appid': str(next_id),
        'userid': userid,
        'trackingid': tracking_id,
        'type': type,
        'subtype': subtype,
        'status': status,
        'createdat': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return csv_store.insert_row('applications', app_data)

def get_application_by_id(appid: str) -> dict | None:
    return csv_store.find_by_id('applications', 'appid', appid)

def get_application_by_tracking(trackingid: str) -> dict | None:
    apps = csv_store.filter_rows('applications', trackingid=trackingid)
    return apps[0] if apps else None

def get_all_applications() -> list[dict]:
    return csv_store.read_all('applications')

def get_applications_for_user(userid: str) -> list[dict]:
    return csv_store.filter_rows('applications', userid=userid)

def update_application_status(appid: str, new_status: str) -> dict | None:
    return csv_store.update_row('applications', 'appid', appid, {'status': new_status})


# --- Documents ---

def create_document(appid: str, filename: str, filetype: str, sizebytes: int, storagepath: str) -> dict:
    docs = csv_store.read_all('documents')
    next_id = csv_store._get_next_id(docs, 'docid')
    
    doc_data = {
        'docid': str(next_id),
        'appid': appid,
        'filename': filename,
        'filetype': filetype,
        'sizebytes': str(sizebytes),
        'storagepath': storagepath
    }
    return csv_store.insert_row('documents', doc_data)

def get_documents_for_app(appid: str) -> list[dict]:
    return csv_store.filter_rows('documents', appid=appid)


# --- Deliveries ---

def create_delivery(appid: str, courierid: str, trackingnumber: str, status: str) -> dict:
    deliveries = csv_store.read_all('deliveries')
    next_id = csv_store._get_next_id(deliveries, 'deliveryid')
    
    delivery_data = {
        'deliveryid': str(next_id),
        'appid': appid,
        'courierid': courierid,
        'trackingnumber': trackingnumber,
        'currentstatus': status,
        'lastupdate': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return csv_store.insert_row('deliveries', delivery_data)

def get_delivery_for_app(appid: str) -> dict | None:
    deliveries = csv_store.filter_rows('deliveries', appid=appid)
    return deliveries[0] if deliveries else None

def update_delivery_status(deliveryid: str, new_status: str) -> dict | None:
    return csv_store.update_row('deliveries', 'deliveryid', deliveryid, {
        'currentstatus': new_status,
        'lastupdate': time.strftime('%Y-%m-%d %H:%M:%S')
    })


# --- Notifications ---

def create_notification(userid: str, templateid: str, medium: str) -> dict:
    notifs = csv_store.read_all('notifications')
    next_id = csv_store._get_next_id(notifs, 'notifid')
    
    notif_data = {
        'notifid': str(next_id),
        'userid': userid,
        'templateid': templateid,
        'medium': medium,
        'sentat': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return csv_store.insert_row('notifications', notif_data)

def get_notifications_for_user(userid: str) -> list[dict]:
    return csv_store.filter_rows('notifications', userid=userid)


# --- Audit Logs ---

def log_action(actorid: str, action: str, targetid: str, details_json: str = "{}"):
    logs = csv_store.read_all('audit_logs')
    next_id = csv_store._get_next_id(logs, 'logid')
    
    log_data = {
        'logid': str(next_id),
        'actorid': actorid,
        'action': action,
        'targetid': targetid,
        'details': details_json,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    csv_store.insert_row('audit_logs', log_data)
