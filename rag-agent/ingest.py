"""
文档入库脚本 - RAG 的第 1 步

流程：
1. 读取 docs/ 目录下的所有 .txt 文件
2. 将文档切成小块（chunk）
3. 用 OpenAI Embedding 模型将文本转成向量
4. 存入 ChromaDB 向量数据库

运行方式：
    python ingest.py

只需要运行一次（或文档更新后重新运行）
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ChromaDB 数据存储路径
CHROMA_PATH = "./chroma_db"
# 文档目录
DOCS_PATH = "./docs"


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        print("❌ 请先在 .env 文件中设置 OPENAI_API_KEY")
        return

    # ============================================================
    # 第 1 步：加载文档
    # ============================================================
    print("📄 加载文档...")
    loader = DirectoryLoader(
        DOCS_PATH,
        glob="**/*.txt",           # 匹配所有 .txt 文件
        loader_cls=TextLoader,     # 用 TextLoader 读取
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"   加载了 {len(documents)} 个文档")

    # ============================================================
    # 第 2 步：切片
    # 为什么要切片？因为 LLM 的上下文窗口有限，
    # 而且检索时小块文本比整篇文档更精准
    # ============================================================
    print("✂️  切分文档...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # 每块最多 500 个字符
        chunk_overlap=50,     # 相邻块重叠 50 个字符，避免切断语义
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   切分为 {len(chunks)} 个文本块")

    # ============================================================
    # 第 3 步：向量化 + 存入 ChromaDB
    # OpenAI Embedding 模型会把文本转成一个数字向量（如 1536 维）
    # 语义相近的文本，向量也相近，这就是检索的基础
    # ============================================================
    print("🔢 向量化并存入 ChromaDB...")

    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_kwargs = {"model": embedding_model, "api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        embedding_kwargs["base_url"] = base_url

    embeddings = OpenAIEmbeddings(**embedding_kwargs)

    # 如果已有旧数据，先清除
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)
        print("   清除旧数据")

    # 创建向量数据库并存入数据
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
    )

    print(f"✅ 完成！{len(chunks)} 个文本块已存入 {CHROMA_PATH}")
    print("   现在可以运行 python query.py 开始问答")


if __name__ == "__main__":
    main()
