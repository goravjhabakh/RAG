from services.mongo import MongoDBClient
from services.log import LOGGER
from datetime import datetime

logger = LOGGER.get_logger()
client = MongoDBClient.get_client()
db = client['documents']
collection = db['history']

async def load_chat_history(user_id: int):
    try:
        hist = collection.find_one({'user_id': user_id})
        if hist == None: return []

        history = []
        for msg in hist['messages']:
            role = msg['role']
            content = msg['content']
            history.append({role: content})
        logger.info(f'Loaded {len(history)} messages')
        return history

    except Exception as e:
        logger.error(f'Failed to load chat history for user {user_id}: {str(e)}')

async def save_chat_history(user_id:int, query: str, answer:str, query_time: datetime, answer_time: datetime):
    try:
        msgs = [
            {'role': 'user', 'content': query, 'timestamp': query_time},
            {'role': 'ai', 'content': answer, 'timestamp': answer_time}
        ]

        with open('chat_history.txt', 'a') as f:
            f.write(f'user: {query} \nai: {answer}\n')

        res = collection.update_one(
            {'user_id': user_id},
            {'$push': {'messages': {'$each': msgs}}},
            upsert=True
        )

        if res.upserted_id: logger.info(f'Created new chat history for user {user_id}')
        logger.info(f'Saved chat history for user {user_id}')
    
    except Exception as e:
        logger.error(f'Failed to save chat history due to error: {str(e)}')