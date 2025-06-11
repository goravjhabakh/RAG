from services.mongo import MongoDBClient
from pymongo.operations import SearchIndexModel
import asyncio

client = MongoDBClient.get_client()

async def update_search_index(db_name: str = 'documents', collection_name: str = 'test', index_name: str = 'vindex'):
    db = client[db_name]
    collection = db[collection_name]

    existing_index = list(collection.list_search_indexes())
    index_exists = any(idx['name'] == index_name for idx in existing_index)
    if index_exists:
        collection.drop_search_index(index_name)

        # Wait until its deleted
        while True:
            await asyncio.sleep(1)
            existing_index = list(collection.list_search_indexes())
            index_exists = any(idx['name'] == index_name for idx in existing_index)
            if not index_exists: break


    
    index_model = SearchIndexModel( 
        definition={
            "fields": [ 
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                }
            ],
        },
        name=index_name,
        type='vectorSearch'
    )

    collection.create_search_index(model=index_model)