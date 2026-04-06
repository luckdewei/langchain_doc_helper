from langchain_pinecone import PineconeVectorStore
from backend.config import INDEX_NAME, PINECONE_API_KEY, TOP_K
from backend.embedding import get_embeddings


def get_retriever(top_k: int = None):
    embeddings = get_embeddings()
    vectorstore = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY,
    )
    k = top_k or TOP_K
    return vectorstore.as_retriever(search_kwargs={"k": k})


def search_with_sources(query: str, top_k: int = None):
    retriever = get_retriever(top_k)
    docs = retriever.invoke(query)
    sources = []
    seen_urls = set()
    for doc in docs:
        url = doc.metadata.get("source_url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            sources.append({
                "url": url,
                "title": doc.metadata.get("title", url),
                "content": doc.page_content,
            })
    return docs, sources
