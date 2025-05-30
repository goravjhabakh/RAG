from pymongo import MongoClient
from typing import Optional

# Creating a wrapper around MongoClient class to ensure its instantiated only once
class MongoDBClient:
    _instance: Optional[MongoClient] = None # Initially no class of mongoclient is instantiated

    # In this method if _instance is none i.e, MongoClient class is not instantiated then a new object is instatiated and is returned
    # If an object of MongoClient was already created it returns that object instead of creating a new one
    @classmethod 
    def get_client(cls, uri: str = "mongodb+srv://goravjhabakh1301:rarr9Zkq42OJ5csB@rag.1vunq22.mongodb.net/") -> MongoClient:
        if cls._instance is None:
            cls._instance = MongoClient(uri)
        return cls._instance