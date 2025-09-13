from typing import TypedDict
from langgraph.graph import StateGraph, START, END

#defien el estado del agente
class State(TypedDict):
    my_var: str
    customer_name: str

#define nodes (agent == node)
def node_1(state: State) -> State:
    state["my_var"] = "Hello"
    state["customer_name"] = "Alex"
    return state

def node_2(state: State) -> State:
    customer_name = state["customer_name"]
    state["my_var"] = f"Hello {customer_name}"
    return state

def node_3(state: State) -> State:
    return state

#Define Grafo
builder = StateGraph(State)

#Define nodos (key, name)
builder.add_node('node_2',node_2)
builder.add_node('node_1',node_1)
builder.add_node('node_3',node_3)

#Define la secuencia de los agentes para este caso 
builder.add_edge(START,'node_1')
builder.add_edge('node_1','node_2')
builder.add_edge('node_2','node_3')
builder.add_edge('node_3',END)

#Tambien para definir la secuencia se debe utilizar:
# graph.add_conditional_edges()

#compilar
graph = builder.compile()