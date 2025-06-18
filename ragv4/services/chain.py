import json
from langdetect import detect, DetectorFactory, LangDetectException
from services.log import LOGGER
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

logger = LOGGER.get_logger()
DetectorFactory.seed = 0

class CheckQuery():
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
    
    def is_valid_language(self, query:str) -> bool:
        try:
            _ = detect(query)
            return True
        except LangDetectException as e:
            logger.error(f'Language Error: {e}')
            return False
    
    def check_query(self, query:str) -> bool:
        prompt = f"""Analyse the following query and classify if it contains any of these: spam, gibberish, cusswords, any offensive 
        content or just random numbers. Basically it should look like a proper query. Respond in a python dictionary format with: 
        "is_valid": true/false, "reason": short explanation.Dont give in code format just give in normal string format with curly 
        brackets and if valid is false then make explanation like You query contains this or something like that,
        
        Query: {query}
        """
        response = self.llm.invoke(prompt)
        answer = json.loads(response.content)
        logger.info(answer)

        return answer

    def invoke(self, query:str) -> str:
        if not self.is_valid_language(query): return {'is_valid': False, 'reason': 'Unable to process this query'}
        return self.check_query(query)
    
class GetCheckQuery:
    _instance: Optional[CheckQuery] = None 

    @classmethod 
    def get_class(cls, llm) -> CheckQuery:
        if cls._instance is None:
            cls._instance = CheckQuery(llm=llm)
        return cls._instance