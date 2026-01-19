from config import *
from pathlib import Path
from typing import Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.retrievers import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv("OPENAI_API_KEY"):
    print("cargado correctamente")
#Retriver

class RagRetriver:

    def __init__(self,chroma_path: str = "/chroma_db"):
        self.chroma_path = Path(chroma_path)
        self.embedding = OpenAIEmbeddings(model=str(EMBEDDINGS_MODEL))
        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
        self.vectorstore = None
        self.retriever = None
        
        #se ejecutara siempre que se llame a la clase
        self._load_vectorstore()

    
    def _load_vectorstore(self):
        """Cargar VectorStore existente"""
        try:
            #verificar si existe vector store
            if not self.chroma_path.exists():
                print(f"No existe la ruta especificada: {self.chroma_path}")
                return
            
            #Carga una base de datos existente desde disco
            self.vectorstore = Chroma(
                embedding_function=self.embedding,
                persist_directory=self.chroma_path,
                collection_name="proyectos_knowledge"
            )

            #Configurar retriever
            self.retriever = MultiQueryRetriever.from_llm(
                retriever=self.vectorstore.as_retriever(
                    search_type = "similarity",
                    search_kwargs = {"k":1}
                ),
                llm= self.llm,
                prompt = self._multy_query_prompt()
            )

            print("cargado correctamente desde disco vectorstore")
        
        except Exception as e:
            print(f"Error cargando vectorstore:\n{str(e)}")
            self.vectorstore = None
            self.retriever = None
    
    def _multy_query_prompt(self):
        """Prompt personalizado para MultiQueryRetriever"""
        prompt = ChatPromptTemplate.from_template(
        """
        Eres un experto en bucar en una bese vectorial de conocimiento.
        Tu trabajo es generar multiples preguntas para recuperar de una base de conocimientos tecnica.
        Genera 3 versiones de la pregunta origianl, tenienso encuenta:
        - Sinónimos técnicos
        - Diferentes formas de expresar el mismo problema
        - Variación en terminos técnicos

        Consulta original: 
        {question}
        
        Versiones alternativas:  
        """
        )

        return prompt
    
    def buscar(self, consulta: str) -> dict[str, Any]: 
        """Utiliza las preguntas de multiqueryretriever para buscar en los docs"""

        if not self.retriever:
            return {
                "respuesta": "El sistema RAG no esta disponible",
                "fuentes": []
            }
        #invocar documentos, tambien realiza el multiqueryretriever
        documents = self.retriever.invoke(consulta)

        if not documents:
            return {
                "respuesta": "No existe documentos para el sistema RAG",
                "fuentes":[],
                "pages": []
            }

        #Extraer contexto y metadata
        contexts_partes = []
        fuentes = []
        pages = []

        for i, doc in enumerate(documents[:2]):
            context = doc.page_content.strip()
            if context:
                contexts_partes.append(context)

                #Extrae fuentes
                fuente = doc.metadata.get('filename',f'doc_{i}')
                if fuente not in fuentes:
                    fuentes.append(fuente)
                
                #Extrae Número de página
                page = doc.metadata.get('page_label',None)
                if page:
                    pages.append(page)
            
            if not context:
                return {
                    "respuesta": "No existe contexto en los Documents",
                    "fuentes": fuentes,
                    "pages": pages
                }

        contexto = "\n\n".join(contexts_partes)
        respuesta = self._generar_respuesta(consulta, contexto)
        
        return {
            "respuesta": respuesta,
            "fuentes": fuentes,
            "pages": pages
        }
    
    def _generar_respuesta(self, consulta: str, contexto: str):
        """Generar la respuesta con datos de vectorstore y llm"""
        prompt = ChatPromptTemplate.from_template(
        """
        Eres un experto en respondet unicamente con el contexto de la base de conocimiento.
        Instrucciones:
        - Proporciona una respuesta clara, directa y útil
        - Si el contexto no contiene información suficiente, dilo claramente
        - No agregues nada al final como por ejemplo: si necesitas más detalles, no dudes en preguntar.
        - No inventes información que no esté en el contexto

        Contexto de la base de conocimiento: {contexto}

        Consulta del usuario: {consulta}
        """
        )

        try:
            respuesta = self.llm.invoke(prompt.format(consulta=consulta, contexto=contexto))
            return respuesta.content.strip()
        except Exception as e:
            return "No se pudo procesar la consulta con el contexto de vectorstore"


#Test
def main():

    documents_retriever = RagRetriver(chroma_path=VDB_PATH)
    print(documents_retriever.buscar("Quién es gerente de marketing ?"))

if __name__ == "__main__":
    main()

