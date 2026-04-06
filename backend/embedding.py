from langchain_openai import OpenAIEmbeddings
from backend.config import MODELSCOPE_BASE_URL, MODELSCOPE_API_KEY


def get_embeddings():
    return OpenAIEmbeddings(
        base_url=MODELSCOPE_BASE_URL,
        api_key=MODELSCOPE_API_KEY,
        model="Qwen/Qwen3-Embedding-8B",
        show_progress_bar=False,
        chunk_size=50,
        retry_min_seconds=10,
        dimensions=1536,
    )
