import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rag_chain import build_rag_chain

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

chain = build_rag_chain()


class QuestionRequest(BaseModel):
    question: str


@app.post("/chat")
async def chat(req: QuestionRequest):
    async def generate():
        async for chunk in chain.astream({"question": req.question}):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
