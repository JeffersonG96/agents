import os
from dotenv import load_dotenv
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import END
from langgraph.graph import StateGraph, START

load_dotenv()
if os.getenv("OPENAI_API_KEY"):
    print("Cargado correctamente")

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "..", "notebooks", "state_db", "exmple.db")
db_path = os.path.normpath(db_path)
conn=sqlite3.connect(db_path,check_same_thread = False)

memory = SqliteSaver(conn)

MODEL = "gpt-4o-mini"
llm = ChatOpenAI(model=MODEL,temperature=0.6)

class State(TypedDict):
    messages: Annotated[list[AnyMessage],add_messages]
    summary: str

#systemMessages
def llamar_modelo(state: State):
    summary = state.get("summary","")

    if summary:
        system_messages = f"Resume la conversación: {summary}"
        messages = [SystemMessage(content = system_messages)] + state["messages"]
    
    else:
        messages = state["messages"]
    
    response = llm.invoke(messages)
    return {"messages": response}

def resumir_conversacion(state: State):
    summary = state.get("summary","")

    if summary:
        summary_message = (f"Este es el resumen hasta ahora: {summary}\n"
                        "Extiende el resumen teniendo encuenta los nuevos mensajes anteriores:")
    else: 
        summary_message = "Crea un resumen de la conversación anterior"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)

    #eliminar todos los mensajes excepto los dos últimos 
    delete_menssage = [RemoveMessage(id = m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages":delete_menssage}

def determinar(state: State):
    """Return the next node to execute"""
    messages = state["messages"]
    if len(messages) > 6:
        return "resumir_conversacion"
    return END

workflow = StateGraph(State)
#define nodos
workflow.add_node("conversacion",llamar_modelo)
workflow.add_node(resumir_conversacion)
#secuencia
workflow.add_edge(START,"conversacion")
workflow.add_conditional_edges("conversacion",determinar)
workflow.add_edge("resumir_conversacion",END)
#compilar
# checkpointer=memory
graph = workflow.compile()

config = {"configurable": {"thread_id":"1"}}