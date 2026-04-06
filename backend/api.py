import asyncio
import json
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, AVAILABLE_MODELS
from backend.llm import get_llm
from backend.retriever import search_with_sources
from backend.doc_ingestion import ingest_documents
from backend.rag_chain import build_rag_chain, build_general_chain, is_langchain_related

app = FastAPI(title="LangChain Doc Helper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    model: str = DEFAULT_LLM_MODEL
    temperature: float = DEFAULT_TEMPERATURE


class IngestRequest(BaseModel):
    urls: list[str] | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None


@app.get("/api/models")
def get_models():
    return {"models": AVAILABLE_MODELS, "default": DEFAULT_LLM_MODEL}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        loop = asyncio.get_event_loop()
        is_lc = await loop.run_in_executor(
            None, lambda: is_langchain_related(req.question, model=req.model)
        )

        if not is_lc:
            chain = build_general_chain(model=req.model, temperature=req.temperature)

            async def general_event_generator():
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: chain.invoke({"question": req.question})
                )
                for char in result:
                    yield f"data: {json.dumps({'type': 'content', 'data': char}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                general_event_generator(), media_type="text/event-stream"
            )

        docs, sources = search_with_sources(req.question)

        if not docs:
            return {
                "answer": "抱歉，在 LangChain 文档中未找到与您的问题相关的内容。请尝试换一种方式提问。",
                "sources": [],
            }

        rag_chain = build_rag_chain(model=req.model, temperature=req.temperature)

        async def event_generator():
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: rag_chain.invoke({"docs": docs, "question": req.question})
            )

            yield f"data: {json.dumps({'type': 'sources', 'data': sources}, ensure_ascii=False)}\n\n"

            for char in result:
                yield f"data: {json.dumps({'type': 'content', 'data': char}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest")
async def ingest(req: IngestRequest = None):
    try:
        urls = req.urls if req else None
        chunk_size = req.chunk_size if req else None
        chunk_overlap = req.chunk_overlap if req else None
        ingest_documents(urls=urls, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return {"status": "success", "message": "Documents ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}
