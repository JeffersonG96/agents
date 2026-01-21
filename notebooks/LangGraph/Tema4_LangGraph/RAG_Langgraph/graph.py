from typing import TypedDict, List, Optional, Annotated,Any
from operator import add
from rag_system import RagRetriver
from config import *
from PIL import Image
import io

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import RemoveMessage, AnyMessage
from langgraph.checkpoint.memory import MemorySaver 



class MyState(TypedDict):
    consulta: str
    respuesta: str
    fuentes: Optional[list]
    pages: Optional[list]
    historial: Annotated[List[AnyMessage], add_messages]
    resumen: Annotated[List[str], add]

class AsistentePersonal():

    def __init__(self):
        self.rag = RagRetriver(chroma_path=VDB_PATH)
        self.llm = ChatOpenAI(model=LLM_MODEL,temperature=0.1)
        self.memory = MemorySaver()
        self.graph = None
    

    #Nodos
    def ejecutar_rag(self, state: MyState) -> dict[str, Any]:
        resultado = self.rag.buscar(state.get('consulta'))
        long = resultado.get('historial')
        print(f"Longitud de historial en ejecuta rag: {long}")

        print(f"")
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
        print(f"Resumen con una longitud de {len(historial)}") 

        if historial:
            prompt = ChatPromptTemplate.from_template(
            """Eres un experto en resumi texto del usuario. 
            Instrucciones:
            - Manten el contexto de la conversación 
            - El resumen no debe pasar de las 35 palabras por resumen

            Este es el historial: {historial}
            """
            )

            try:
                print("="*50)
                resp = self.llm.invoke(prompt.format(historial=historial))
                resumen = resp.content.strip()
                delete_messages = [RemoveMessage(id=m.id) for m in state["historial"][:-2]]
                return {
                "historial": delete_messages,
                "resumen": [resumen]
                }
            except Exception as e:
                print(f"ERROR, no se puede resumir: {e}")
        
        return {
            "historial":["No se encontro mensajes para resumir"]
        }
    
    def eliminar_mensajes(self, state: MyState) -> dict[str, any]:
        """Elimina todos los mensajes menos los últimos dos"""
        return {"historial": state.get('historial')[-2:]}
    
    def decidir_router(self, state: MyState):
        """Verifica la longitud de los mensajes en el historial"""
        resumen = state.get('historial')
        if len(resumen) > 4:
            return "resumir"
        else:
            return END

    def crear_grafo(self):
        """Construye el grafo"""
        grafo = StateGraph(MyState)

        #agregar nodos
        grafo.add_node("consulta", self.ejecutar_rag)
        grafo.add_node("resumir",self.resumir_conversacion)
        grafo.add_node("eliminar",self.eliminar_mensajes)

        #workflow
        grafo.add_edge(START, "consulta")

        grafo.add_conditional_edges("consulta",self.decidir_router, {
            "resumir":"resumir",
            END:END
        })

        grafo.add_edge("resumir",END)

        compiled = grafo.compile(checkpointer=self.memory)

        self.graph = compiled

        # png_bytes = compiled.get_graph().draw_mermaid_png()
        # img = Image.open(io.BytesIO(png_bytes))
        # img.show()

        return self.graph

def main():
    config = {'configurable': {"thread_id":'sesion_1'}}

    asistente = AsistentePersonal()
    resultado = asistente.crear_grafo().invoke({"consulta":"quien es el director de marketing ?"}, 
    config=config )
    print(resultado)

    resultado1 = asistente.crear_grafo().invoke({"consulta":"Quien es el autor de gestion de proyectos?"}, 
    config=config )
    print(resultado1)

    resultado2 = asistente.crear_grafo().invoke({"consulta":"En pocas palabras explica la arquitectura de un sistema embebido?"}, 
    config=config )
    print(resultado2)
 
    resultado3 = asistente.crear_grafo().invoke({"consulta":"en 10 palabras explica el modulo de E/S"}, 
    config=config )
    print(resultado3)

    resultado4 = asistente.crear_grafo().invoke({"consulta":"que es el chasis reconfigurable ?"}, 
    config=config )
    print(resultado4)
    


    
if __name__ == "__main__":
    main()
