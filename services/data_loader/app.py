import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# === ENV ===
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_HOST = os.getenv("MONGO_HOST", "mongo-app")
MONGO_DB   = os.getenv("MONGO_INITDB_DATABASE", "mydb")
MONGO_USER = os.getenv("MONGO_USERNAME")
MONGO_PASS = os.getenv("MONGO_PASSWORD")



uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_DB}"

client = MongoClient(uri)
db = client[MONGO_DB]
users = db["users"]


app = FastAPI()

class UserIn(BaseModel):
    name: str
    email: EmailStr

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr

@app.get("/healthz")
def healthz():
    try:
        client.admin.command("ping")
        return {"status": "ok"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    try:
        result = users.insert_one(user.dict())
        doc = users.find_one({"_id": result.inserted_id})
        return UserOut(id=str(doc["_id"]), name=doc["name"], email=doc["email"])
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def list_users():
    try:
        return [UserOut(id=str(doc["_id"]), name=doc["name"], email=doc["email"]) for doc in users.find()]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))
