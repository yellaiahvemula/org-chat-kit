"""FastAPI application — org chat API."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Add python/ to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from agent.agent import run_agent
from shared.config import ROOT_DIR, get_org_config_dir, list_orgs, load_branding

app = FastAPI(title="Org Chat Kit", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGO = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

DEMO_USERS = {
    ("msme-demo", "officer@msme-demo.gov.in"): ("officer123", "officer"),
    ("msme-demo", "user@example.com"): ("user123", "user"),
}

_audit_log: list[dict] = []


class LoginRequest(BaseModel):
    email: str
    password: str
    org_id: str = "msme-demo"


class ChatRequest(BaseModel):
    message: str
    org_id: str = "msme-demo"


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    escalated: bool
    tools_used: list[str]


def create_token(email: str, org_id: str, role: str) -> str:
    payload = {"sub": email, "org_id": org_id, "role": role,
               "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    if not creds:
        return None
    try:
        return jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(401, "Invalid token")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/orgs")
def get_orgs():
    return {"orgs": list_orgs()}


@app.get("/api/org/{org_id}/branding")
def branding(org_id: str):
    try:
        return load_branding(org_id)
    except FileNotFoundError:
        raise HTTPException(404, "Org not found")


@app.post("/api/auth/login")
def login(req: LoginRequest):
    key = (req.org_id, req.email)
    if key in DEMO_USERS:
        pw, role = DEMO_USERS[key]
        if req.password == pw:
            return {"token": create_token(req.email, req.org_id, role),
                    "user": {"email": req.email, "role": role, "org_id": req.org_id}}
    raise HTTPException(401, "Invalid credentials")


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user: Optional[dict] = Depends(get_current_user)):
    try:
        get_org_config_dir(req.org_id)
    except FileNotFoundError:
        raise HTTPException(404, "Org not found")
    result = run_agent(req.org_id, req.message)
    entry = {"org_id": req.org_id, "user": user.get("sub") if user else None,
             "query": req.message, "response": result.answer, "confidence": result.confidence,
             "tools": [t.get("tool") for t in result.tools_called], "at": datetime.now(timezone.utc).isoformat()}
    _audit_log.append(entry)
    return ChatResponse(answer=result.answer, confidence=result.confidence, escalated=result.escalated,
                        tools_used=[t.get("tool", "") for t in result.tools_called if t.get("tool")])


@app.get("/api/audit")
def audit(org_id: str = "msme-demo", user: Optional[dict] = Depends(get_current_user)):
    if not user or user.get("role") != "officer":
        raise HTTPException(403, "Officer access required")
    logs = [l for l in _audit_log if l["org_id"] == org_id][-50:]
    return {"logs": logs}


def main():
    import uvicorn
    port = int(os.environ.get("API_PORT", "8000"))
    uvicorn.run("app.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
