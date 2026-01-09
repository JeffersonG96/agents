from langgraph.graph import StateGraph, END,START
from typing import TypedDict
from PIL import Image
import io
#Estructura del estado
class State(TypedDict):
    numero: int
    resultado: str

#Crear el grafo del estado 
graph = StateGraph(State)

#Funciones de los nodos 
def caso_par(state):
    return {'resultado':'El número es par'}

def caso_impar(state):
    return {'resultado':'El número es impar'}

#Añadir los nodos al grafo
graph.add_node("par",caso_par)
graph.add_node("impar",caso_impar)

#Definir la función routing para decidir la rama de ejecución
def decidir_rama(state):
    if state['numero'] % 2 == 0:
        return "par"
    else: 
        return "impar"

#añadir el edge condicional al worflow
graph.add_conditional_edges(START,decidir_rama, {'par':'par','impar':'impar'})
graph.add_edge("par",END)
graph.add_edge("impar",END)

#compilar 
compiled = graph.compile()

png_bytes = compiled.get_graph().draw_mermaid_png()
img = Image.open(io.BytesIO(png_bytes))
img.show()

#probar el Grafo
print(compiled.invoke({'numero':2}).get('resultado'))