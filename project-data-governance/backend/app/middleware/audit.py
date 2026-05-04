from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.db import SessionLocal
from app.models.audit_log import AuditLog
from datetime import datetime
import time


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        db = SessionLocal()

        endpoint = request.url.path
        method = request.method

        # ngambil IP address
        ip_address = request.client.host if request.client else "unknown"

        # user
        user_email = "anonymous"

        # ngambil token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload:
                    user_email = payload.get("sub", "unknown")
            except:
                pass

        # request
        response = await call_next(request)

        # ngitung waktu
        latency_ms = int((time.time() - start_time) * 1000)

        # ngambil status code
        status_code = response.status_code

        # nyimpan log
        log = AuditLog(
            user_email=user_email,
            action="API_CALL",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )

        db.add(log)
        db.commit()
        db.close()

        return response