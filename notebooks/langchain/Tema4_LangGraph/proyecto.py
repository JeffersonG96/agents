from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, List
import os
from tkinter import TK, filedialog
import openai

#configurar llm
llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)

# Estructura del estado 
class State(TypedDict):
    notes: str
    participants: List[str]
    topics: List[str]
    action_items: List[str]
    minutes: str
    summary: str

# ============ NODOS DEL WORKFLOW =?==============
def extract_participants(state: State) -> State:
    """Extrae los participantes de la reunion."""
    prompt = f""" 
    De las siguientes notas de reunion, extrae solo los nombres de los participantes. 
    Notas: {state.get("notes")}
    Responde ÚNICAMENTE con una lista de nombres separados poir comas, sin explicaciones adicionales. Ejemplo: Juan García, María López, Carlos Ruiz
    """
    response = llm.invoke(prompt)
    participants = 