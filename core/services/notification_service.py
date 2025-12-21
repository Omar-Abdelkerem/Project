from core.storage import repository

STATUS_TEMPLATES = {
    "APPLICATION_SUBMITTED": "APP_SUBMIT",
    "APPLICATION_APPROVED": "APP_APPROVE",
    "APPLICATION_REJECTED": "APP_REJECT",
    "DELIVERY_OUT": "DEL_OUT",
    "DELIVERY_DONE": "DEL_DONE"
}

def send_status_notification(userid: str, templateid: str, medium: str = "email") -> dict:
    """
    Creates a notification record and simulates sending.
    
    Args:
        userid: The ID of the user to notify.
        templateid: The template ID (e.g., 'APP_SUBMIT', or use keys from STATUS_TEMPLATES).
                    If a detailed status key is passed (e.g. 'APPLICATION_SUBMITTED'), 
                    it maps it to the short code.
        medium: 'email' or 'sms'.
    """
    # Map long status to short template code if exists, else use as is
    mapped_template = STATUS_TEMPLATES.get(templateid, templateid)
    
    print(f"[Authorized] Sending {mapped_template} to user {userid} via {medium}")
    
    return repository.create_notification(userid, mapped_template, medium)
