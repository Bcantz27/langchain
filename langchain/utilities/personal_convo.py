from langchain.chains.llm import LLMChain, PromptTemplate
from langchain.llms.base import BaseLLM
from typing import List

template = """{ai_desc}

    {ai_name} is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, {ai_name} is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

    {ai_name} is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, {ai_name} is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

    Overall, {ai_name} is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, {ai_name} is here to assist.

    {history}
    {human_name}: {human_input}
    {ai_name}:"""

class PersonalConvo:
    def __init__(self, llm: BaseLLM, chat_history: List[str] = [], ai_name: str = "Assistant", ai_desc: str = "Assistant is a large language model", human_name: str = "Human"):
        prompt = PromptTemplate(
            input_variables=["ai_desc", "ai_name", "human_name", "history", "human_input"], 
            template=template
        )
        self.convo_chain = LLMChain(
            llm=llm, 
            prompt=prompt
        )
        self.chat_history = chat_history
        self.ai_name = ai_name
        self.ai_desc = ai_desc
        self.human_name = human_name

    def run(self, query: str) -> str:
        history = ""
        for chat in self.chat_history:
            history += chat + '\n\n'

        return self.convo_chain.run({"ai_desc": self.ai_desc, "ai_name": self.ai_name, "human_name": self.human_name, "history": history, "human_input": query})