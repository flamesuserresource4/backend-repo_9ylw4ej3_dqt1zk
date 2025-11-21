import os
import hashlib
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from database import db, create_document, get_documents
from schemas import User, BlogPost, ContactMessage

app = FastAPI(title="SaaS Landing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def hash_password(password: str) -> str:
    salt = os.getenv("AUTH_SALT", "flames_salt")
    return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()


@app.get("/")
def root():
    return {"message": "SaaS Landing Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


@app.post("/api/auth/signup")
def signup(payload: SignupRequest):
    # Check existing user
    existing = db["user"].find_one({"email": payload.email}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    user_id = create_document("user", user)
    return {"ok": True, "user_id": user_id}


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    doc = db["user"].find_one({"email": payload.email})
    if not doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if doc.get("password_hash") != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Simple session token (demo)
    token = hashlib.sha256(f"{doc['_id']}{os.getenv('AUTH_SALT','flames_salt')}".encode()).hexdigest()
    return {"ok": True, "token": token, "name": doc.get("name"), "email": doc.get("email")}


@app.get("/api/blog", response_model=List[BlogPost])
def list_blog(limit: int = 10):
    docs = get_documents("blogpost", {}, limit)
    # Convert Mongo docs to pydantic-compatible dicts
    items = []
    for d in docs:
        d.pop("_id", None)
        items.append(BlogPost(**d))
    return items


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@app.post("/api/contact")
def contact(payload: ContactRequest):
    cm = ContactMessage(**payload.model_dump())
    msg_id = create_document("contactmessage", cm)
    return {"ok": True, "message_id": msg_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
