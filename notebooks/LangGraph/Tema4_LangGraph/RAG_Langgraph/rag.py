from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from typing import List

from pathlib import Path
from config import *
from pprint import pprint

class ProcesarDocumentos:

    def __init__(self, docs_path: str="docs", chroma_path: str = "./chroma_db"):
        self.docs_path = Path(docs_path)
        self.chroma_path = Path(chroma_path)
        self.embeddings = OpenAIEmbeddings
        self.text_spliter = RecursiveCharacterTextSplitter(
            chunk_size = 800,
            chunk_overlap = 120,
            length_function = len,
            separators = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

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
        
        print(f"Total de chunks creados: {len(chunks)}")
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
            persist_directory=str(self.chroma_path)
        )

        return vectorstore





def main(): 
    """Función principal para probar"""
    print("Iniciando prueba")

    processor = ProcesarDocumentos(docs_path=DOCUMENTS_PATH,vdb_path=VDB_PATH)
    
    documents = processor.load_documents()
    print(f"Total de documentos: {len(documents)}")

    chunks = processor.split_documents(documents)
    print(F"Total de chunks: {len(chunks)}")

    

   

if __name__ == "__main__":
    main()

    

