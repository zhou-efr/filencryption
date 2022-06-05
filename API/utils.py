from pymongo import MongoClient
import os


def connect_db():
    client = MongoClient(os.getenv('MONGODB_FILE_ENCRYPTION_URI'))
    db = client.filencryption
    return db


def get_user_db():
    db = connect_db()
    users = db.users
    return users


def get_transfers_db():
    db = connect_db()
    transfers = db.transfers
    return transfers
