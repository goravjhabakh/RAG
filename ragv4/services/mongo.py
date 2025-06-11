from pymongo import MongoClient
from typing import Optional
from dotenv import load_dotenv
import os 
from services.log import LOGGER

load_dotenv()
logger = LOGGER.get_logger()

# Creating a wrapper around MongoClient class to ensure its instantiated only once
class MongoDBClient:
    _instance: Optional[MongoClient] = None # Initially no class of mongoclient is instantiated

    # In this method if _instance is none i.e, MongoClient class is not instantiated then a new object is instatiated and is returned
    # If an object of MongoClient was already created it returns that object instead of creating a new one
    @classmethod 
    def get_client(cls, uri: str = os.getenv('MONGO_URI')) -> MongoClient:
        if cls._instance is None:
            logger.info(f'Connecting to URI: {os.getenv('MONGO_URI')}')
            cls._instance = MongoClient(uri)
            logger.info('Connected...')
        return cls._instance