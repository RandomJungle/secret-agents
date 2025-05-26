from typing import Literal

from langchain_mistralai import ChatMistralAI
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState, START, END

from prompts import (
    ambassador_prompt,
    spy_prompt,
    anti_spy_prompt,
    regular_person_prompt
)

model = ChatMistralAI()

def agent_1(state: MessagesState) -> Command[Literal['agent_2', 'agent_3', 'agent_4', END]]:
    response = model.invoke(
        input=ambassador_prompt
    )
    return Command(
        goto=response['next_agent'],
        update={
            'message': [response['content']]
        }
    )
