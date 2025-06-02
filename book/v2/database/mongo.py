from pymongo import MongoClient
from typing import Optional
from logs.logging import LOGGER

class MongoDB:
    instance: Optional[MongoClient] = None
    logger = LOGGER.get_logger()

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls.instance is None:
            cls.logger.info('Creating new MongoDB instance')
            cls.instance = MongoClient('mongodb://localhost:27017/')
        return cls.instance