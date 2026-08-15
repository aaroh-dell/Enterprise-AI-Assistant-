import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = "backend/rag/documents"
PERSIST_DIR = "backend/rag/chroma_store"


def ingest():
    # Step 1: Load every .txt file in the documents folder
    loader = DirectoryLoader(DOCS_DIR, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    # Step 2: Split each document into smaller chunks
    # chunk_size=500 characters, chunk_overlap=50 keeps some context
    # bleeding between chunks so a fact split across a chunk boundary isn't lost
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    # Step 3: Embed each chunk and store it in Chroma
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )

    print(f"Ingested {len(chunks)} chunks into Chroma at {PERSIST_DIR}")
    return vectorstore


if __name__ == "__main__":
    ingest()