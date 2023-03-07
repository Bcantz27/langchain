from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain, PromptTemplate
from langchain.vectorstores.base import VectorStore
from langchain.utilities.document_search import DocumentSearch
from typing import List

template = """
    Please read the Documents provided below and consider whether it has the answer to the Question.
    Feel free to ignore irrelevant information given in the Documents.
    Your answer must be completly honesty and it is acceptable if you dont know the answer.
    If you do know the answer then provide a detailed response.
    If you dont know the answer say "I could not find any relavant information".

    Documents:
    {documents}

    Question: {question}
    Response:"""

class InternalSearch:
    def __init__(self, vectorstore: VectorStore, number_of_documents: int = 3):
        llm=OpenAI(temperature=0)
        prompt = PromptTemplate(
            input_variables=["documents", "question"], 
            template=template
        )
        self.chain = LLMChain(
            llm=llm, 
            prompt=prompt
        )
        self.vectorstore = vectorstore
        self.number_of_documents = number_of_documents      

    def run(self, question: str) -> str:
        docSearch = DocumentSearch(self.vectorstore, self.number_of_documents)
        docs = docSearch.run(question)
        print(docs)
        return self.chain.run({"question": question, "documents": docs})