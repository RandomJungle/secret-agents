import os
import time
from langchain.chat_models import init_chat_model
from typing import Literal, Optional
from langgraph.graph import StateGraph, START
from dotenv import find_dotenv, load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, END
from langgraph.types import Command


def get_next_node(last_message: BaseMessage, goto: str):
    if '[END]' in last_message.content:
        # Any agent decided the work is done
        return END
    return goto


# Inspector node
def inspector_node(state: MessagesState) -> Command[Literal['suspect', END]]:
    result = inspector_agent.invoke(state)
    goto = get_next_node(result['messages'][-1], 'suspect')
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result['messages'][-1] = HumanMessage(
        content=result['messages'][-1].content, name='inspector'
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            'messages': result['messages'],
        },
        goto=goto,
    )


# Suspect node
def suspect_node(state: MessagesState) -> Command[Literal['inspector', END]]:
    result = suspect_agent.invoke(state)
    goto = get_next_node(result['messages'][-1], 'inspector')
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result['messages'][-1] = HumanMessage(
        content=result['messages'][-1].content, name='suspect'
    )
    return Command(
        update={
            # share internal message history of chart agent with other agents
            'messages': result['messages'],
        },
        goto=goto,
    )


def stream_graph_updates(
        user_input: str,
        output_file_path: str,
        recursion_limit: Optional[int] = 10):
    output = ''
    for event in graph.stream(
            {
                'messages': [{'role': 'user', 'content': user_input}]
            },
            {"recursion_limit": recursion_limit}
    ):
        for key, value in event.items():
            output += f'{key}: '
            content = value['messages'][-1].content
            print(f'{key}:', content)
            output += content
            with open(output_file_path, 'w') as output_file:
                output_file.write(output)
            if key == 'suspect' and '[END]' in output:
                return output
            print('*' * 100)
            output += '\n' + ('*' * 100) + '\n'
    return output


if __name__ == '__main__':

    load_dotenv(find_dotenv())

    llm = init_chat_model('mistral-large-latest')

    # Inspector agent
    inspector_agent = create_react_agent(
        llm,
        tools=[],
        prompt='''You are role-playing as Ken Pulaski, an inspector paying a visit to a suspect on a murder investigation. You are an old and disillusioned cop who has seen too many things. You questions about the case at hand, limiting yourself to one question at a time. When you feel the suspect has answered all of your questions, add [END] at the end of your last statement. DO NOT add the [END] statement if the suspect hasn't answered all of the questions, or if you have subsequent questions arising from their statement
        ''',
    )

    # Suspect agent
    suspect_agent = create_react_agent(
        llm,
        tools=[],
        prompt='''You are role-playing as Gigi Monaco, a suspect in a murder case. You work night shifts in a cabaret in a dark and foggy town. You are questioned by a detective about your alibi on the night of a murder. Answer the questions of the detective while staying in character, improvise answers that don't incriminate you while trying to learn more about what happened.
        ''',
    )

    workflow = StateGraph(MessagesState)
    workflow.add_node('inspector', inspector_node)
    workflow.add_node('suspect', suspect_node)

    workflow.add_edge(START, 'inspector')
    graph = workflow.compile()
    graph.get_graph().draw_mermaid_png(
        output_file_path=os.path.join(
            os.getenv('OUTPUT_DIR_PATH'),
            'neo-noir-graph.png'
        )
    )

    intro = 'Hello, this is the police'
    discussion = stream_graph_updates(
        user_input=intro,
        output_file_path=os.path.join(
            os.getenv('OUTPUT_DIR_PATH'),
            f'discussion_{round(time.time())}.txt'
        ),
        recursion_limit=10
    )