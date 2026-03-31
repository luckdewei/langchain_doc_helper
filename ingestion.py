import asyncio
import os
from typing import List

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders.sitemap import SitemapLoader

from logger import Colors, log_error, log_header, log_info, log_success, log_warning

load_dotenv()
os.environ["USER_AGENT"] = "langchain-doc-helper/1.0"

BASE_URL = "https://api-inference.modelscope.cn/v1"

embeddings = OpenAIEmbeddings(
    base_url=BASE_URL,
    model="Qwen/Qwen3-Embedding-4B",
    dimensions=1536,
    show_progress_bar=False,
    chunk_size=32,  # embedding 每次处理的文本数，调小
    retry_min_seconds=10,
    max_retries=5,  # 遇到限速自动重试
)

vectorstore = PineconeVectorStore(
    index_name=os.environ["INDEX_NAME"],
    embedding=embeddings,
)

# vectorstore.delete(delete_all=True)
# print("Pinecone index 已清空")


async def ingest() -> List[Document]:
    log_header("爬取文档中...")
    loader = SitemapLoader(
        web_path="https://docs.langchain.com/sitemap.xml",
        requests_per_second=10,  # 别太激进
        requests_kwargs={"timeout": 30},
    )
    docs = await asyncio.to_thread(loader.load)
    log_success(f"共爬取 {len(docs)} 个页面")
    return docs


async def index_documents_async(
    documents: List[Document],
    batch_size: int = 50,
    sleep_between: float = 1.0,
    max_retries: int = 3,
):
    log_header("向量存储阶段")
    log_info(f"准备写入 {len(documents)} 个文档", Colors.DARKCYAN)

    batches = [
        documents[i : i + batch_size] for i in range(0, len(documents), batch_size)
    ]
    log_info(f"共 {len(batches)} 个批次，每批 {batch_size} 个文档（串行执行）")

    successful = 0
    for i, batch in enumerate(batches):
        batch_num = i + 1
        for attempt in range(1, max_retries + 1):
            try:
                await vectorstore.aadd_documents(batch)
                log_success(
                    f"批次 {batch_num}/{len(batches)} 完成（{len(batch)} 个文档）"
                )
                await asyncio.sleep(sleep_between)
                successful += 1
                break
            except Exception as e:
                if attempt == max_retries:
                    log_error(
                        f"批次 {batch_num} 放弃（重试 {max_retries} 次后仍失败）: {e}"
                    )
                else:
                    wait = attempt * 2
                    log_warning(
                        f"批次 {batch_num} 第 {attempt} 次失败，{wait}s 后重试: {e}"
                    )
                    await asyncio.sleep(wait)

    if successful == len(batches):
        log_success(f"全部 {successful}/{len(batches)} 批次写入成功")
    else:
        log_warning(
            f"成功 {successful}/{len(batches)} 批次，{len(batches) - successful} 个批次失败"
        )


async def main():
    all_docs = await ingest()

    log_header("文档分块阶段")
    log_info(
        f"处理 {len(all_docs)} 个文档，chunk_size=1000，overlap=100", Colors.YELLOW
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # 4000 太大，embedding 效果差，推荐 500-1000
        chunk_overlap=100,
    )
    splitted_docs = text_splitter.split_documents(all_docs)
    log_success(f"共创建 {len(splitted_docs)} 个 chunk")

    await index_documents_async(
        documents=splitted_docs,
        batch_size=500,  # 每批 50 个 chunk
        sleep_between=2.0,  # 每批间隔 2 秒
    )

    log_header("导入完成")
    log_success("🎉 文档导入完成！")
    log_info(f"   • 页面爬取: {len(all_docs)}")
    log_info(f"   • chunk 数量: {len(splitted_docs)}")


if __name__ == "__main__":
    asyncio.run(main())
