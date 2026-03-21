"""
RAG 问答脚本 - RAG 的第 2 步

流程：
1. 用户提问
2. 将问题转成向量
3. 从 ChromaDB 中检索最相关的文本块
4. 将检索到的内容 + 用户问题一起发给 LLM
5. LLM 基于检索到的内容回答问题

运行方式：
    python query.py

前提：先运行 python ingest.py 完成文档入库
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

CHROMA_PATH = "./chroma_db"

# RAG 的 prompt 模板
# 关键：把检索到的内容放在 context 里，让 LLM 基于这些内容回答
RAG_PROMPT = ChatPromptTemplate.from_template("""
你是一个有用的 AI 助手。请根据以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请如实说明。
回答时使用中文。

参考资料：
{context}

用户问题：{question}
""")


def create_rag_chain():
    """创建 RAG 问答链"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        raise ValueError("请在 .env 文件中设置 OPENAI_API_KEY")

    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError("向量数据库不存在，请先运行 python ingest.py")

    # 加载 Embedding 模型（和入库时用同一个）
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_kwargs = {"model": embedding_model, "api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        embedding_kwargs["base_url"] = base_url

    embeddings = OpenAIEmbeddings(**embedding_kwargs)

    # 加载 ChromaDB
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # 创建检索器：每次检索最相关的 3 个文本块
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # 创建 LLM
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm_kwargs = {"model": model, "api_key": api_key}
    if base_url:
        llm_kwargs["base_url"] = base_url
    llm = ChatOpenAI(**llm_kwargs)

    return retriever, llm


def ask(retriever, llm, question: str) -> str:
    """
    RAG 问答的核心流程：
    1. 检索相关文档
    2. 拼接 prompt
    3. 调用 LLM
    """
    # 第 1 步：检索相关文本块
    docs = retriever.invoke(question)

    # 第 2 步：把检索到的内容拼成一个字符串
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])

    # 第 3 步：填充 prompt 模板
    prompt = RAG_PROMPT.format(context=context, question=question)

    # 第 4 步：调用 LLM
    response = llm.invoke(prompt)

    # 显示检索到的来源（方便调试）
    sources = set()
    for doc in docs:
        if doc.metadata.get("source"):
            sources.add(doc.metadata["source"])

    return response.content, sources


def main():
    print("🔍 初始化 RAG 系统...")
    retriever, llm = create_rag_chain()

    print("=" * 50)
    print("🤖 RAG Agent 已启动")
    print("   输入问题，Agent 会从本地文档中检索并回答")
    print("   输入 'quit' 退出")
    print("=" * 50)
    print()

    while True:
        try:
            question = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 再见！")
            break

        if not question:
            continue
        if question.lower() == "quit":
            print("👋 再见！")
            break

        answer, sources = ask(retriever, llm, question)
        print(f"\nAgent: {answer}")
        if sources:
            print(f"📚 参考来源: {', '.join(sources)}")
        print()


if __name__ == "__main__":
    main()
