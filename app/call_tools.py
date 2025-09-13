
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

#Tools
def tool_multiply(a: int, b:int) -> int:
    """Multiplica a y b
    Args: 
        a (int): primero
        b (int): segundo
    Returns:
        int: el producto de a y b   
    """
    return a * b

def tool_add(a: int, b:int) -> int:
    """suma a y b
    
    Args: 
        a (int): primero
        b (int): segundo  

    Returns:
        int: la suma de a y b

    """
    return a + b

def tool_divide(a: int, b: int) -> float:
    """Divide a y b

    Args: 
        a (int): primero
        b (int): segundo 

    Returns:
        int: el resultado de la division de a y b 
    """
    return a / b


tools = [tool_add, tool_divide, tool_multiply]
llm=ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

system_msg = SystemMessage(content="eres un asistente útil cuya tarea es realicar operaciones aritmeticas con un conjunto de datos de entrada")

#node
def assistant(state: State) -> State:
    return {"messages": [llm_with_tools.invoke([system_msg] + state["messages"])]}

#Graph
builder = StateGraph(State)

#nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

#Define edge (secuencia)
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools","assistant")

#Compile
graph=builder.compile()

