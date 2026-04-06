from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.llm import get_llm
from backend.retriever import search_with_sources


CLASSIFIER_PROMPT = """你是一个问题分类器。判断用户的问题是否与 LangChain 框架相关。

如果问题与 LangChain、LangGraph、Deep Agents、AI Agent、向量数据库、Embedding、RAG、LLM 应用开发相关，回答 YES。
如果是通用问题（如天气、数学、编程基础、日常生活等），回答 NO。

只回答 YES 或 NO，不要有其他内容。

用户问题：{question}"""

SYSTEM_PROMPT = """你是一个 LangChain 文档助手，专门帮助用户查阅 LangChain 的 API 和使用方法。

回答要求：
1. 必须使用中文回答，即使用户用英文提问
2. 基于提供的参考文档内容回答，不要编造信息
3. 在回答末尾列出参考的文档来源网址，格式为：
   📄 来源：
   - [文档标题](网址)
   - [文档标题](网址)
4. 如果参考文档内容不足以完整回答问题，请如实告知用户，并说明文档中已有的相关内容
5. 回答要结构清晰、条理分明，适当使用代码块展示 API 用法

参考文档内容：
{context}"""

GENERAL_PROMPT = (
    """你是一个 AI 助手。请用中文回答用户的问题，回答要准确、简洁、有帮助。"""
)

HUMAN_PROMPT = "{question}"


def is_langchain_related(
    question: str, model: str = None, temperature: float = 0
) -> bool:
    """判断问题是否与 LangChain 相关"""
    llm = get_llm(model=model, temperature=temperature, streaming=False)
    prompt = ChatPromptTemplate.from_messages([("human", CLASSIFIER_PROMPT)])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question}).strip().upper()
    return "YES" in result


def build_rag_chain(model: str = None, temperature: float = None):
    llm = get_llm(
        model=model,
        temperature=temperature,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    def format_docs(docs):
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": lambda x: format_docs(x["docs"]),
            "question": lambda x: x["question"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def build_general_chain(model: str = None, temperature: float = None):
    llm = get_llm(
        model=model,
        temperature=temperature,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GENERAL_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    return chain


def query_langchain(question: str, model: str = None, temperature: float = None):
    docs, sources = search_with_sources(question)

    if not docs:
        return {
            "answer": "抱歉，在 LangChain 文档中未找到与您的问题相关的内容。请尝试换一种方式提问。",
            "sources": sources,
        }

    rag_chain = build_rag_chain(model=model, temperature=temperature)

    answer = rag_chain.invoke({"docs": docs, "question": question})

    return {
        "answer": answer,
        "sources": sources,
    }
