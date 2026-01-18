from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from typing import List
import logging

from pathlib import Path
from config import *
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv("OPENAI_API_KEY"):
    print("cargado correctamente")

class ProcesarDocumentos:

    def __init__(self, docs_path: str="docs", chroma_path: str = "./chroma_db"):
        self.docs_path = Path(docs_path)
        self.chroma_path = Path(chroma_path)
        self.embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
        self.text_spliter = RecursiveCharacterTextSplitter(
            chunk_size = 800,
            chunk_overlap = 120,
            length_function = len,
            separators = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    #     )
    # logging.getLogger("langchain.embeddings").setLevel(logging.INFO)
    
    def load_documents(self):
        """Cargar documentos"""
        print("Iniciando cargador de documentos")

        loader = DirectoryLoader(
            path = self.docs_path,
            glob = "*.pdf",
            loader_cls= PyPDFLoader,
            show_progress=True,
        )

        documents = loader.load()

        #Enriquecer los metadatos
        for doc in documents:
            filename = Path(doc.metadata["source"]).stem  #solo nombre de archivo
            doc.metadata.update({
                "filename":filename,
            })

        return documents
    
    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Divide los documentos en chunks"""
        print("iniciando split de documentos")

        chunks = self.text_spliter.split_documents(documents)

        #Enriquecer metadatos de los chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id":i,
                "chunk_size": len(chunk.page_content)
            })
        
        return chunks
    
    def create_vectorstore(self, documents: list[Document]) -> Chroma:
        """Crear Embeddings y  caragar a chroma"""
        print("Iniciando VectorStore")

        if self.chroma_path.exists():
            import shutil
            print("Borrando directorio existente de CHROMA")
            shutil.rmtree(path=str(self.chroma_path))

        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name="proyectos_knowledge",
            persist_directory=str(self.chroma_path),
            
        )
        logging.info("Creado correctamente vectorstore")

        return vectorstore
    
    def loag_exiting_vectorstore(self):
        """Cargar VectorStore existinte"""
        if not self.chroma_path.exists():
            raise FileNotFoundError(f"No se encontro vectorstore en: {self.chroma_path}")
        
        vectorstore = Chroma(
            collection_name="proyectos_knowledge",
            embedding_function=self.embeddings,
            persist_directory=str(self.chroma_path)
        )

        return vectorstore
    
    def setup_rag(self, force_rebuild: bool = False):
        """Configurar el sistema RAG completo"""

        #Verificar si existe y no forzar rebuilld
        if self.chroma_path.exists() and not force_rebuild:
            print("VectorStore encontrado")
            return self.loag_exiting_vectorstore()
        
        #Cargar documentos
        documents = self.load_documents()
        if not documents:
            print("No se encontraron documentos")
            return None
        #Dividir en chunks los docs cargados
        chunks = self.split_documents(documents=documents)

        #Guardar en VectorStore
        vectorstore = self.create_vectorstore(chunks)

        print("Sistema RAG configurado exitosamente")
        return vectorstore
    
def main(): 
    """Función principal para probar"""
    print("Iniciando prueba")

    processor = ProcesarDocumentos(docs_path=DOCUMENTS_PATH,chroma_path=VDB_PATH)
    
    processor.setup_rag(force_rebuild=True)

if __name__ == "__main__":
    main()

    

