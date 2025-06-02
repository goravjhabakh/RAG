from bson.objectid import ObjectId
from typing import Optional,Dict,Any
from database.mongo import MongoDB
from logs.logging import LOGGER

logger = LOGGER.get_logger()

client = MongoDB.get_client()
db = client['books']
collection = db['books']

def create_book(book: Dict[str, Any]) -> str:
    res = collection.insert_one(book)
    logger.info(f"Inserted book with ID: {res.inserted_id}")
    return str(res.inserted_id)

def get_book(id: int) -> Optional[Dict[str,Any]]:
    res = collection.find_one({'id': id})
    if res: logger.info(f"Fetched book with id={id}")
    else: logger.warning(f"Book with id={id} not found")
    return res

def get_all_books() -> list:
    books = list(collection.find())
    logger.info(f"Retrieved {len(books)} books from database")
    return books

def update_book(id: int, data: Dict[str,Any]) -> bool:
    res = collection.update_one({'id': id}, {'$set': data})
    logger.info(f"Update book id={id} - Modified: {res.modified_count}")
    return res.modified_count > 0

def patch_book(id: int, data: Dict[str,Any]) -> bool:
    res = collection.update_one({'id': id}, {'$set': data})
    logger.info(f"Patch book id={id} - Modified: {res.modified_count}")
    return res.modified_count > 0

def delete_book(id: int) -> bool:
    res = collection.delete_one({'id': id})
    logger.info(f"Delete book id={id} - Deleted: {res.deleted_count}")
    return res.deleted_count > 0