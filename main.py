import os
from typing import Union

from pymongo import DESCENDING
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

from utils import get_user_db, get_transfers_db

app = FastAPI()


class User(BaseModel):
    name: str
    public: int


class Transfer(BaseModel):
    from_user: str
    to_user: str
    cipher: str
    sendAt: str


@app.get("/")
def welcome():
    return {"message": "file encryption API"}


@app.get("/base")
def base():
    return {"common": int(os.getenv('BASE_KEY')), "base": int(os.getenv('BASE_MODULUS'))}


@app.get("/users")
def get_users():
    users_db = get_user_db()
    users = users_db.find()
    users_list = []

    for user in users:
        users_list.append({
            "name": user["name"],
            "public": user["public"]
        })
    return {"users": users_list}


@app.get("/user/{name}")
def get_user(name: str):
    users = get_user_db()
    user = users.find_one({"name": name}, sort=[('_id', DESCENDING)])
    return {
        "name": user["name"],
        "public": user["public"]
    }


@app.post("/user")
def create_user(user: User):
    users = get_user_db()
    if users.find_one({"name": user.name}):
        return {"message": "user already exists"}
    users.insert_one(user.dict())
    return {"user": user.dict()}


@app.get("/transfers")
def get_transfers():
    transfers_db = get_transfers_db()
    transfers = transfers_db.find()

    transfers_list = []
    for transfer in transfers:
        transfers_list.append({
            "from_user": transfer["from_user"],
            "to_user": transfer["to_user"],
            "cipher": transfer["cipher"],
            "sendAt": transfer["sendAt"]
        })

    return {"transfers": transfers_list}


@app.get("/transfers/{to_user}")
def get_transfers(to_user: str):
    transfers_db = get_transfers_db()
    transfers = transfers_db.find({"to_user": to_user})

    transfers_list = []
    for transfer in transfers:
        transfers_list.append({
            "from_user": transfer["from_user"],
            "to_user": transfer["to_user"],
            "cipher": transfer["cipher"],
            "sendAt": transfer["sendAt"]
        })

    return {"transfers": transfers_list}


@app.get("/transfer/{to_user}")
def get_transfer(to_user: str):
    transfers = get_transfers_db()
    transfer = transfers.find_one({"to_user": to_user}, sort=[('_id', DESCENDING)])
    return {
        "from_user": transfer["from_user"],
        "to_user": transfer["to_user"],
        "cipher": transfer["cipher"],
        "sendAt": transfer["sendAt"]
    }


@app.post("/transfer")
def create_transfer(transfer: Transfer):
    transfers = get_transfers_db()
    transfers.insert_one(transfer.dict())
    return {"transfer": transfer.dict()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
