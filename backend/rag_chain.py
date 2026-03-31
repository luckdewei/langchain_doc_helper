import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter
from langchain_tavily import TavilySearch

BASE_URL = "https://api-inference.modelscope.cn/v1"


def format_docs(docs):
    """格式化检索到的文档，附带来源 URL"""
    formatted = []
    for i, doc in enumerate(docs):
        # SitemapLoader / 不同 loader 对元数据字段命名可能不同
        source = (
            doc.metadata.get("source")
            or doc.metadata.get("loc")
            or doc.metadata.get("url")
            or "未知来源"
        )
        content = doc.page_content.strip()
        formatted.append(f"[文档 {i+1}] 来源: {source}\n{content}")
    return "\n\n---\n\n".join(formatted)


def format_web_results(results: dict) -> str:
    """把 Tavily 的搜索结果格式化成可注入 LLM 的上下文。"""
    formatted = []
    web_results = results.get("results") or []
    for i, r in enumerate(web_results[:4], 1):
        url = r.get("url") or "unknown"
        title = r.get("title") or ""
        content = (r.get("content") or r.get("raw_content") or "").strip()
        # 防止上下文爆炸：只保留前置片段
        content = content[:1800]
        formatted.append(
            f"[网页检索 {i}] 来源: {url}{'（' + title + '）' if title else ''}\n{content}"
        )
    return "\n\n---\n\n".join(formatted)


async def maybe_enrich_context(question: str, context: str) -> str:
    """
    本地 RAG 优先；若关键字段缺失，则用网页检索补充（例如 init_chat_model 参数页）。
    """
    q = (question or "").lower()
    ctx = (context or "").lower()

    # 只对“明确指向函数签名/配置项”的问题做兜底，避免增加无谓成本
    if "init_chat_model" not in q:
        return context

    # 如果本地上下文里没有关键配置字段，就尝试用网页补充 API reference
    if (
        "configurable_fields" in ctx
        or "model_provider" in ctx
        or "config_prefix" in ctx
    ):
        return context

    tavily = TavilySearch(
        max_results=3,
        include_domains=[
            "reference.langchain.com",
            "api.python.langchain.com",
            "python.langchain.com",
        ],
        include_answer=False,
        include_raw_content="text",
        search_depth="basic",
    )

    # 直接用问题做检索，便于覆盖不同语言/表述
    res = await tavily.ainvoke({"query": question})
    web_context = format_web_results(res)
    if not web_context:
        return context

    return f"{context}\n\n---\n\n{web_context}"


async def _enrich_context_from_tuple(question_and_context: tuple[str, str]) -> str:
    question, context = question_and_context
    return await maybe_enrich_context(question, context)


def build_rag_chain():
    embeddings = OpenAIEmbeddings(
        base_url=BASE_URL,
        model="Qwen/Qwen3-Embedding-4B",
        dimensions=1536,
        chunk_size=50,
    )

    vectorstore = PineconeVectorStore(
        index_name=os.environ["INDEX_NAME"],
        embedding=embeddings,
    )

    # chunk_size=4000 内容较长，k=5 足够，避免 context 过长超出模型限制
    retriever = vectorstore.as_retriever(
        # 用更高的召回 + 更合适的样本选择，提升“检索是否命中关键片段”的概率
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 25},
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """你是一个专业的 LangChain 中文文档助手。

## 约束
- 必须全程使用中文回答（代码除外）
- 只能基于“参考文档片段（含可能的网页检索补充）”中的信息回答；禁止编造不存在的 API/类名/参数名/行为细节
- 若参考文档仍不足以支撑某结论：必须明确说明“参考文档未覆盖”，并给出如何进一步查找（不要臆测）

## 回答结构（尽量完整但不过度冗长）
1) 直接回答（1-2 句话，说明结论/要点）
2) 解释与展开：把参考文档里的关键点拆开讲清楚（2-5 段，包含必要的背景/流程/注意事项）
3) 代码示例：当参考文档出现了可复用示例时提供，否则使用网页检索补充代码示例，必须要用代码示例，但是不要编造代码
4) 拓展延伸：常见坑、最佳实践、相关概念或替代方案（同样必须来自参考文档；不足则标注“参考文档未覆盖”）
5) 参考文档：列出你实际用到的 URL，格式为：
  > 参考文档：
  > - [页面标题或描述](url)

## 引用标注
- 当你提出某条关键论断时，在该段末尾追加引用编号，例如“（依据文档 [文档 1]、[文档 3]）”
- 若你使用了网页检索信息，也请在引用中体现，例如“（依据网页检索 [网页检索 1]）”
""",
            ),
            (
                "human",
                """问题：
{question}

参考文档（仅限这些片段）：
{context}
""",
            ),
        ]
    )

    llm = ChatOpenAI(
        base_url=BASE_URL,
        model="deepseek-ai/DeepSeek-V3.2",
        streaming=True,
        temperature=0.1,
        max_completion_tokens=1200,
    )

    chain = (
        RunnablePassthrough.assign(
            context=itemgetter("question") | retriever | format_docs
        )
        | RunnablePassthrough.assign(
            context=(
                itemgetter("question", "context")
                | RunnableLambda(_enrich_context_from_tuple)
            )
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
