from typing import TypedDict, List, Optional, Annotated,Any
from operator import add
from rag_system import RagRetriver
from config import *

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



class MyState(TypedDict):
    consulta: str
    respuesta: str
    categoria: Optional[str]
    fuentes: list
    pages: list
    historial: Annotated[List[str], add]

class AsistentePersonal():

    def __init__(self):
        self.rag = RagRetriver(chroma_path=VDB_PATH)
        self.llm = ChatOpenAI(model=LLM_MODEL,temperature=0.1)
        self.graph = None
    

    #Nodos
    def ejecutar_rag(self, state: MyState) -> dict[str, Any]:
        resultado = self.rag.buscar(state.get('consulta'))
        return {
            "respuesta": resultado.get('respuesta'),
            "fuentes": resultado.get('fuentes'),
            "pages": resultado.get('pages'),
            "historial": [
                f"Se consulto al sistem RAG  y se obtuvo: {resultado.get('respuesta')}",
                f"Fuentes identificadas: {resultado.get('fuentes')} de las paginas: {resultado.get('pages')}"
            ]
        }
    
    def resumir_conversacion(self, state: MyState) -> dict[str, Any]:
        historial = state.get('historial')

        if historial:
            prompt = ChatPromptTemplate.from_template(
            """Has un resumen corto de 
            """
            )


