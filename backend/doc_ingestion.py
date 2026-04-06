import httpx
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from backend.config import (
    LANGCHAIN_DOC_URLS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    INDEX_NAME,
    PINECONE_API_KEY,
)
from backend.embedding import get_embeddings
from backend.logger import log_info, log_success, log_error, log_header


def fetch_doc_content(url: str) -> str:
    try:
        resp = httpx.get(url, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
        )
        if main_content:
            return main_content.get_text(separator="\n", strip=True)
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        log_error(f"Failed to fetch {url}: {e}")
        return ""


def ingest_documents(
    urls: list[str] = None, chunk_size: int = None, chunk_overlap: int = None
):
    urls = urls or LANGCHAIN_DOC_URLS
    chunk_size = chunk_size or CHUNK_SIZE
    chunk_overlap = chunk_overlap or CHUNK_OVERLAP

    log_header("Starting Document Ingestion")

    log_info(f"Fetching {len(urls)} documents...")
    docs = []
    for i, url in enumerate(urls):
        log_info(f"[{i+1}/{len(urls)}] Loading: {url}")
        try:
            loader = WebBaseLoader(url)
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.metadata["source_url"] = url
            docs.extend(loaded_docs)
            log_success(f"Loaded: {url}")
        except Exception as e:
            log_error(f"Failed to load {url}: {e}")
            continue

    if not docs:
        log_error("No documents loaded. Aborting.")
        return

    log_info(f"Total documents loaded: {len(docs)}")

    log_info(
        f"Splitting documents (chunk_size={chunk_size}, overlap={chunk_overlap})..."
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    splits = text_splitter.split_documents(docs)
    log_success(f"Total chunks: {len(splits)}")

    log_info(f"Embedding and storing to Pinecone index: {INDEX_NAME}...")
    embeddings = get_embeddings()
    vectorstore = PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=INDEX_NAME,
    )
    log_success(f"Successfully stored {len(splits)} chunks to Pinecone.")
    log_header("Ingestion Complete")


if __name__ == "__main__":
    ingest_documents()
