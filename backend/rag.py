import os
import logging
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma

from config import get_shared_client, EMBEDDING_MODEL_ID, CHROMA_PERSIST_DIR, PDF_DIRECTORY

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self):
        self.vectorstore = None
        self.embeddings = None
        self._initialized = False
    
    def setup(self):
        """Initialize the RAG pipeline"""
        if self._initialized:
            return
            
        logger.info("📚 [RAG] Setting up pipeline...")
        
        # Create embeddings using shared client
        self.embeddings = BedrockEmbeddings(
            client=get_shared_client(),
            model_id=EMBEDDING_MODEL_ID
        )
        
        # Load existing vectorstore or create new one
        if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
            logger.info("📚 [RAG] Loading existing ChromaDB...")
            self.vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
        else:
            self._create_vectorstore()
        
        self._initialized = True
        logger.info("✅ [RAG] Ready!")
    
    def _create_vectorstore(self):
        """Create new vectorstore from PDFs"""
        logger.info(f"📄 [RAG] Loading PDFs from {PDF_DIRECTORY}...")
        
        if not os.path.exists(PDF_DIRECTORY):
            os.makedirs(PDF_DIRECTORY, exist_ok=True)
            raise Exception(f"No PDFs found! Add PDFs to {PDF_DIRECTORY}")
        
        loader = PyPDFDirectoryLoader(PDF_DIRECTORY)
        documents = loader.load()
        
        if not documents:
            raise Exception(f"No PDFs found in {PDF_DIRECTORY}")
        
        logger.info(f"📄 [RAG] Loaded {len(documents)} pages from PDFs")
        
        # Split documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)
        logger.info(f"✂️  [RAG] Split into {len(chunks)} chunks")
        
        # Create vectorstore
        logger.info("🔢 [RAG] Creating embeddings (this may take a moment)...")
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )
        logger.info("✅ [RAG] ChromaDB created and persisted!")
    
    def search(self, query: str, k: int = 4) -> tuple[str, list[str]]:
        """
        Search knowledge base and return formatted context.
        Returns: (context_string, list_of_sources)
        """
        if not self._initialized:
            self.setup()
        
        docs = self.vectorstore.similarity_search(query, k=k)
        
        if not docs:
            logger.info("📭 [RAG] No relevant documents found")
            return "No relevant information found in knowledge base.", []
        
        # Collect unique sources
        sources = []
        context_parts = []
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown").split("/")[-1]
            page = doc.metadata.get("page", "?")
            
            if source not in sources:
                sources.append(source)
            
            context_parts.append(f"[Source: {source}, Page {page}]\n{doc.page_content}")
        
        # Log which files were used
        logger.info(f"📖 [RAG] Found {len(docs)} relevant chunks from: {', '.join(sources)}")
        
        return "\n\n---\n\n".join(context_parts), sources
    
    def get_retriever(self, k: int = 4):
        """Get retriever for chain usage"""
        if not self._initialized:
            self.setup()
        return self.vectorstore.as_retriever(search_kwargs={"k": k})


# Global instance
rag = RAGPipeline()
