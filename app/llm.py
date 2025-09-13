from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END

MODEL = "gpt-4o-mini"
llm = ChatOpenAI(model=MODEL,temperature=0.6)
llm.invoke("hola como estas")


class MyState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


system_message = SystemMessage(content="Eres un asistente de ventas de celulares, respondes en pocas palabras, se breve y consiso")

#node 1
def node_llm(state: MyState) -> MyState:
    return {"messages": [llm.invoke([system_message] + state["messages"])]}


#Define Grafo
builder = StateGraph(MyState)

#Define nodos (key, name)
builder.add_node('node_llm',node_llm)

#Define la secuencia de los agentes para este caso 
builder.add_edge(START,'node_llm')
builder.add_edge('node_llm',END)

#Tambien para definir la secuencia se debe utilizar:
# graph.add_conditional_edges()

#compilar
graph = builder.compile()
