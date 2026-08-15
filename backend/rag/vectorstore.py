import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PERSIST_DIR = "backend/rag/chroma_store"

_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

_vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=_embeddings,
)


def search_policies(query: str, k: int = 3):
    """Search the policy vector store and return the top k most relevant chunks."""
    results = _vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in results]