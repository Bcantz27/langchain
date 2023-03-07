from langchain.chains.llm import LLMChain, PromptTemplate
from langchain.llms.base import BaseLLM
from typing import List

template = """You are given a chat log between {ai_name} and {human_name}. 
    Answer the question provided using ONLY the chat log.
    Feel free to ignore irrelevant information in the chat log that is not related to the question.
    If you cannot determine the answer to the question response "I could not find any information"

    Chat Log:
    {history}
    
    Question: {question}
    Response:"""

class ChatHistorySearch:
    def __init__(self, llm: BaseLLM, chat_history: List[str] = [], ai_name: str = "Assistant", human_name: str = "Human"):
        prompt = PromptTemplate(
            input_variables=["ai_name", "human_name", "history", "question"], 
            template=template
        )
        self.convo_chain = LLMChain(
            llm=llm, 
            prompt=prompt
        )
        self.chat_history = chat_history
        self.ai_name = ai_name
        self.human_name = human_name

    def run(self, question: str) -> str:
        history = ""
        for chat in self.chat_history:
            history += chat + '\n\n'

        return self.convo_chain.run({"ai_name": self.ai_name, "human_name": self.human_name, "history": history, "question": question})