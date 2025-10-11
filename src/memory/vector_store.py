from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

class AgentMemory:
    """
    A singleton class to manage the agent's vector store memory.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Initializing Agent Memory...")
            cls._instance = super(AgentMemory, cls).__new__(cls)
            
            # 1. SETUP EMBEDDINGS using Sentence Transformers (local and private)
            model_name = "all-MiniLM-L6-v2"  # A popular, fast, and effective model
            model_kwargs = {'device': 'cpu'} # Use 'cuda' for GPU
            encode_kwargs = {'normalize_embeddings': False}
            
            embedding_function = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
            # 2. SETUP VECTOR STORE (ChromaDB)
            client = chromadb.Client() # In-memory
            
            cls._instance.vector_store = Chroma(
                client=client,
                collection_name="code_documentation_memory",
                embedding_function=embedding_function,
            )
            
            # 3. SETUP TEXT SPLITTER
            cls._instance.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
        return cls._instance

    def add_content(self, content: str, metadata: dict):
        """Splits text and adds it to the vector store."""
        docs = self.text_splitter.create_documents([content], metadatas=[metadata])
        self.vector_store.add_documents(docs)
        print(f"Added content from '{metadata.get('source')}' to memory.")

    def search_content(self, query: str, k: int = 3) -> list[str]:
        """Queries the memory for relevant information."""
        print(f"Querying memory for: '{query}'")
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

# Create a singleton instance for the rest of the application to use
memory_instance = AgentMemory()