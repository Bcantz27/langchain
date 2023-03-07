from langchain.vectorstores.base import VectorStore

class DocumentSearch:
    def __init__(self, vectorstore: VectorStore, number_of_documents: int = 3):
        self.vectorstore = vectorstore
        self.number_of_documents = number_of_documents

    def run(self, query: str) -> str:
        docs = self.vectorstore.similarity_search(query, self.number_of_documents)
        content = ''
        for doc in docs:
            content += doc.page_content + '\n\n'
        return content