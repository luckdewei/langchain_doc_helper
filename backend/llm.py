from langchain_openai import ChatOpenAI
from backend.config import MODELSCOPE_BASE_URL, MODELSCOPE_API_KEY, DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE


def get_llm(model: str = DEFAULT_LLM_MODEL, temperature: float = DEFAULT_TEMPERATURE, streaming: bool = True):
    return ChatOpenAI(
        openai_api_base=MODELSCOPE_BASE_URL,
        openai_api_key=MODELSCOPE_API_KEY,
        model=model,
        temperature=temperature,
        streaming=streaming,
    )
