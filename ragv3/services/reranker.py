from langchain_core.retrievers import BaseRetriever
from sentence_transformers import CrossEncoder
from pydantic import Field
from typing import List
from langchain_core.documents import Document

class RerankRetriever(BaseRetriever):
    retriever: BaseRetriever = Field(...)
    reranker: CrossEncoder = Field(...)
    top_k: int = 3

    def _get_relevant_documents(self, query: str) -> List[Document]:
        initial_docs = self.retriever.invoke(query)
        pairs = [(query, doc.page_content) for doc in initial_docs]
        scores = self.reranker.predict(pairs)
        reranked = sorted(zip(scores, initial_docs), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in reranked[:self.top_k]]