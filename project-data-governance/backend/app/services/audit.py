from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_action(db: Session, user_email: str, action: str, endpoint: str, method: str):
    log = AuditLog(
        user_email=user_email,
        action=action,
        endpoint=endpoint,
        method=method
    )
    db.add(log)
    db.commit()