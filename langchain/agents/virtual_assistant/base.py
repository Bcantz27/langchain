"""Attempt to implement MRKL systems as described in arxiv.org/pdf/2205.00445.pdf."""
from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple
import logging
logger = logging.getLogger()
from langchain.agents.agent import Agent
from langchain.agents.virtual_assistant.prompt import FORMAT_INSTRUCTIONS, PREFIX, SUFFIX
from langchain.agents.tools import Tool
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

FINAL_ANSWER_ACTION = "Final Answer:"

def get_action_and_input(llm_output: str) -> Tuple[str, str]:
    """Parse out the action and input from the LLM output.

    Note: if you're specifying a custom prompt for the ZeroShotAgent,
    you will need to ensure that it meets the following Regex requirements.
    The string starting with "Action:" and the following string starting
    with "Action Input:" should be separated by a newline.
    """
    if FINAL_ANSWER_ACTION in llm_output:
        return "Final Answer", llm_output.split(FINAL_ANSWER_ACTION)[-1].strip()
    regex = r"Action: (.*?)\nAction Input: (.*)"
    match = re.search(regex, llm_output, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse LLM output: `{llm_output}`")
    action = match.group(1).strip()
    action_input = match.group(2)
    return action, action_input.strip(" ").strip('"')


class VirtualAssistant(Agent):
    """Agent for the MRKL chain."""

    @property
    def _agent_type(self) -> str:
        """Return Identifier of agent type."""
        return "virtual-assistant"

    @property
    def observation_prefix(self) -> str:
        """Prefix to append the observation with."""
        return "Observation: "

    @property
    def llm_prefix(self) -> str:
        """Prefix to append the llm call with."""
        return "Thought:"

    @classmethod
    def create_prompt(
        cls,
        tools: List[Tool],
        chat_history: List[str] = [],
        ai_name: str = "Assistant",
        ai_desc: str = "Assistant is a large language model",
        human_name: str = "Human",
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        input_variables: Optional[List[str]] = None,
    ) -> PromptTemplate:
        """Create prompt in the style of the zero shot agent.

        Args:
            tools: List of tools the agent will have access to, used to format the
                prompt.
            prefix: String to put before the list of tools.
            suffix: String to put after the list of tools.
            input_variables: List of input variables the final prompt will expect.

        Returns:
            A PromptTemplate with the template assembled from the pieces here.
        """
        tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
        tool_names = ", ".join([tool.name for tool in tools])
        format_instructions = FORMAT_INSTRUCTIONS.format(tool_names=tool_names)
        history = ""
        if len(chat_history) > 0: 
            history = "Current conversation:"
        for chat in chat_history:
            history += chat + '\n\n'
        prefix = PREFIX.format(ai_name=ai_name, ai_desc=ai_desc,history=history, human_name=human_name)
        template = "\n\n".join([prefix, tool_strings, format_instructions, suffix])
        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        return PromptTemplate(template=template, input_variables=input_variables)

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLLM,
        tools: List[Tool],
        chat_history: List[str] = [],
        ai_name: str = "Assistant",
        ai_desc: str = "Assistant is a large language model",
        human_name: str = "Human",
        callback_manager: Optional[BaseCallbackManager] = None,
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        input_variables: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Agent:
        """Construct an agent from an LLM and tools."""
        cls._validate_tools(tools)
        prompt = cls.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=input_variables,
            chat_history=chat_history,
            ai_name=ai_name,
            ai_desc=ai_desc,
            human_name=human_name,
        )
        print(prompt)
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        return cls(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)

    @classmethod
    def _validate_tools(cls, tools: List[Tool]) -> None:
        for tool in tools:
            if tool.description is None:
                raise ValueError(
                    f"Got a tool {tool.name} without a description. For this agent, "
                    f"a description must always be provided."
                )

    def _extract_tool_and_input(self, text: str) -> Optional[Tuple[str, str]]:
        return get_action_and_input(text)
