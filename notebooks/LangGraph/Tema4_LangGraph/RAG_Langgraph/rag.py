from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from pathlib import Path
from config import *

class ProcesarDocumentos:

    def __init__(self, docs_path: str="docs", vdb_path: str = "./chroma_db"):
        self.docs_path = Path(docs_path)
        self.vdb_path = Path(vdb_path)
        self.embeddings = OpenAIEmbeddings
        self.text_spliter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            length_function = len,
            separators = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    def load_documents(self):
        """Cargar documentos"""
        print("Iniciando cargador de documentos")

        loader = DirectoryLoader(
            path = self.docs_path,
            glob = "*.md",
            loader_cls= TextLoader,
            show_progress=True,
            loader_kwargs= {"encoding": "utf-8"}
        )

        documents = loader.load()

        #Enriquecer los metadatos
        for doc in documents:
            filename = Path(doc.metadata["source"]).stem  #solo nombre de archivo
            doc.metadata.update({
                "filename":filename,
                "doc_type":self._get_doc_type(filename)
            })

        return documents

    def _get_doc_type(self, filename: str) -> str:
        """Determina el tipo de documento basado en el nombre."""
        if "faq" in filename.lower():
            return "faq"
        elif "manual" in filename.lower():
            return "manual"
        elif "troubleshooting" in filename.lower():
            return "troubleshooting"
        else:
            return "general"

def main(): 
    """Función principal para probar"""
    print("Iniciando prueba")

    processor = ProcesarDocumentos(docs_path=DOCUMENTS_PATH,vdb_path=VDB_PATH)

    print(processor.load_documents())


if __name__ == "__main__":
    main()

    

