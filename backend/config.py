import os
from dotenv import load_dotenv

load_dotenv()

MODELSCOPE_BASE_URL = os.getenv(
    "MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1"
)
MODELSCOPE_API_KEY = os.getenv("MODELSCOPE_API_KEY", "")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
INDEX_NAME = os.getenv("INDEX_NAME", "langchain-doc-index")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "5"))

DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "deepseek-ai/DeepSeek-V3.2")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))

LANGCHAIN_DOC_URLS = [
    # LangChain 核心
    "https://docs.langchain.com/oss/python/langchain/overview",
    "https://docs.langchain.com/oss/python/langchain/install",
    "https://docs.langchain.com/oss/python/langchain/quickstart",
    "https://docs.langchain.com/oss/python/langchain/models",
    "https://docs.langchain.com/oss/python/langchain/messages",
    "https://docs.langchain.com/oss/python/langchain/agents",
    "https://docs.langchain.com/oss/python/langchain/tools",
    "https://docs.langchain.com/oss/python/langchain/tools/built-in",
    "https://docs.langchain.com/oss/python/langchain/structured-output",
    "https://docs.langchain.com/oss/python/langchain/sequences",
    "https://docs.langchain.com/oss/python/langchain/retrievers",
    "https://docs.langchain.com/oss/python/langchain/memory",
    "https://docs.langchain.com/oss/python/langchain/middleware",
    "https://docs.langchain.com/oss/python/langchain/middleware/built-in",
    "https://docs.langchain.com/oss/python/langchain/prompt-templates",
    "https://docs.langchain.com/oss/python/langchain/output-parsers",
    "https://docs.langchain.com/oss/python/langchain/expression-language",
    # LangGraph
    "https://docs.langchain.com/oss/python/langgraph/overview",
    "https://docs.langchain.com/oss/python/langgraph/quickstart",
    "https://docs.langchain.com/oss/python/langgraph/install",
    "https://docs.langchain.com/oss/python/langgraph/graphs",
    "https://docs.langchain.com/oss/python/langgraph/nodes",
    "https://docs.langchain.com/oss/python/langgraph/edges",
    "https://docs.langchain.com/oss/python/langgraph/state",
    "https://docs.langchain.com/oss/python/langgraph/memory",
    "https://docs.langchain.com/oss/python/langgraph/streaming",
    "https://docs.langchain.com/oss/python/langgraph/breakpoints",
    "https://docs.langchain.com/oss/python/langgraph/time-travel",
    "https://docs.langchain.com/oss/python/langgraph/persistence",
    "https://docs.langchain.com/oss/python/langgraph/human-in-the-loop",
    "https://docs.langchain.com/oss/python/langgraph/subgraphs",
    "https://docs.langchain.com/oss/python/langgraph/dynamic",
    "https://docs.langchain.com/oss/python/langgraph/tool-calling",
    "https://docs.langchain.com/oss/python/langgraph/react-agent",
    "https://docs.langchain.com/oss/python/langgraph/map-reduce",
    # Integrations - Providers
    "https://docs.langchain.com/oss/python/integrations/providers/overview",
    "https://docs.langchain.com/oss/python/integrations/chat",
    "https://docs.langchain.com/oss/python/integrations/chat/openai",
    "https://docs.langchain.com/oss/python/integrations/chat/anthropic",
    "https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai",
    "https://docs.langchain.com/oss/python/integrations/chat/azure_chat_openai",
    "https://docs.langchain.com/oss/python/integrations/chat/bedrock",
    "https://docs.langchain.com/oss/python/integrations/chat/huggingface",
    "https://docs.langchain.com/oss/python/integrations/chat/ollama",
    "https://docs.langchain.com/oss/python/integrations/embeddings",
    "https://docs.langchain.com/oss/python/integrations/vectorstores",
    "https://docs.langchain.com/oss/python/integrations/vectorstores/pinecone",
    "https://docs.langchain.com/oss/python/integrations/vectorstores/chroma",
    "https://docs.langchain.com/oss/python/integrations/vectorstores/faiss",
    "https://docs.langchain.com/oss/python/integrations/vectorstores/milvus",
    "https://docs.langchain.com/oss/python/integrations/document_loaders",
    "https://docs.langchain.com/oss/python/integrations/text_splitter",
    "https://docs.langchain.com/oss/python/integrations/retrievers",
    "https://docs.langchain.com/oss/python/integrations/tools",
    "https://docs.langchain.com/oss/python/integrations/memory",
    "https://docs.langchain.com/oss/python/integrations/callbacks",
    "https://docs.langchain.com/oss/python/integrations/llms",
]

AVAILABLE_MODELS = [
    "deepseek-ai/DeepSeek-V3.2",
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen-Plus",
    "Qwen/Qwen-Max",
    "Qwen/Qwen-Turbo",
]
