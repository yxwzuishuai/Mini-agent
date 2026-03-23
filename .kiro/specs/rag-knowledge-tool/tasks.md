# 实现计划：RAG Knowledge Tool

## 概述

将 `fastapi-agent/tools.py` 中硬编码的 `search_knowledge` 工具替换为基于 ChromaDB 向量检索的实现，并更新 `requirements.txt` 添加所需依赖。改动范围最小化：仅修改 `tools.py` 和 `requirements.txt`，保持 `agent.py` 和 `main.py` 不变。

## Tasks

- [x] 1. 更新依赖文件
  - [x] 1.1 在 `fastapi-agent/requirements.txt` 中添加 `chromadb`、`langchain-community`、`langchain-text-splitters` 依赖
    - 在现有依赖列表末尾追加三个新依赖包
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 2. 实现基于 ChromaDB 的 search_knowledge 工具
  - [x] 2.1 在 `fastapi-agent/tools.py` 中新增 `_get_retriever()` 辅助函数
    - 添加 `os` 模块导入和 `langchain_openai.OpenAIEmbeddings`、`langchain_community.vectorstores.Chroma` 导入
    - 实现 `_get_retriever()` 函数：从环境变量 `CHROMA_PATH`（默认 `../rag-agent/chroma_db`）和 `OPENAI_EMBEDDING_MODEL`（默认 `text-embedding-3-small`）读取配置
    - 使用 `os.path.exists()` 检查 ChromaDB 路径是否存在，不存在时抛出 `FileNotFoundError`
    - 初始化 `OpenAIEmbeddings` 并创建 `Chroma` 实例，返回 `retriever`（`search_kwargs={"k": 3}`）
    - 使用模块级变量缓存 retriever 实例，避免重复初始化
    - 复用 `OPENAI_API_KEY` 和可选的 `OPENAI_BASE_URL` 环境变量
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 2.2 替换 `search_knowledge` 函数为基于 ChromaDB 的实现
    - 移除旧的硬编码字典实现
    - 更新工具描述为"从本地文档知识库中检索信息，适用于需要查找技术文档、教程、指南等知识性问题"
    - 调用 `_get_retriever()` 获取 retriever，调用 `retriever.invoke(query)` 检索文档
    - 检索结果为空时返回 `"未找到与 '{query}' 相关的内容"`
    - 正常结果以 `"\n\n---\n\n"` 分隔符拼接各文本块的 `page_content`
    - 捕获 `FileNotFoundError` 返回入库脚本提示信息
    - 捕获 OpenAI API 相关异常返回服务不可用提示
    - 顶层 `except Exception` 捕获所有其他异常，返回错误描述字符串
    - 保持 `ALL_TOOLS` 列表包含 `get_current_time`、`calculate`、`search_knowledge` 三个工具不变
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 6.1, 6.3_

- [x] 3. Checkpoint - 确认代码可运行
  - 确保代码无语法错误，导入正确，ask the user if questions arise.

- [x] 4. 编写单元测试
  - [x] 4.1 创建 `fastapi-agent/test_tools.py`，编写单元测试
    - 测试 `search_knowledge` 使用 `@tool` 装饰器且接受 `query` 参数（需求 1.1）
    - 测试工具描述包含"本地文档知识库"等预期文本（需求 1.2）
    - 测试 `CHROMA_PATH` 未设置时使用默认路径 `../rag-agent/chroma_db`（需求 3.2）
    - 测试 `OPENAI_EMBEDDING_MODEL` 未设置时使用默认值 `text-embedding-3-small`（需求 3.4）
    - 测试 `ALL_TOOLS` 包含三个工具（需求 6.1）
    - 测试 ChromaDB 路径不存在时返回入库脚本提示（需求 4.1）
    - 测试 Embedding API 失败时返回服务不可用信息（需求 4.2）
    - 测试 `requirements.txt` 包含 `chromadb`、`langchain-community`、`langchain-text-splitters`（需求 5.1, 5.2, 5.3）
    - 使用 `unittest.mock` 隔离 ChromaDB 和 OpenAI API 调用
    - _Requirements: 1.1, 1.2, 3.2, 3.4, 4.1, 4.2, 5.1, 5.2, 5.3, 6.1_

  - [ ]* 4.2 编写属性测试：检索结果格式化
    - **Property 1: 检索结果格式化**
    - 使用 `hypothesis` 生成随机非空字符串列表，验证以 `\n\n---\n\n` 分隔符拼接后包含每个原始文本块
    - **Validates: Requirements 2.3**

  - [ ]* 4.3 编写属性测试：检索结果数量上限
    - **Property 2: 检索结果数量上限**
    - 使用 mock ChromaDB 返回不同数量的文档，验证返回结果不超过 3 个文本块
    - **Validates: Requirements 2.4**

  - [ ]* 4.4 编写属性测试：环境变量配置生效
    - **Property 3: 环境变量配置生效**
    - 使用 `hypothesis` 生成随机路径和模型名称，验证工具初始化时使用环境变量值
    - **Validates: Requirements 3.1, 3.3**

  - [ ]* 4.5 编写属性测试：数据库不存在时的错误处理
    - **Property 4: 数据库不存在时的错误处理**
    - 使用 `hypothesis` 生成随机不存在路径，验证返回包含"入库脚本"提示的字符串而非抛出异常
    - **Validates: Requirements 4.1, 4.3**

  - [ ]* 4.6 编写属性测试：异常捕获不泄露
    - **Property 5: 异常捕获不泄露**
    - 使用 mock 模拟检索过程抛出各种异常，验证函数始终返回字符串而非抛出异常
    - **Validates: Requirements 4.3**

- [x] 5. Final checkpoint - 确保所有测试通过
  - 确保所有测试通过，ask the user if questions arise.

## Notes

- 标记 `*` 的任务为可选任务，可跳过以加速 MVP 交付
- 每个任务引用了具体的需求编号，确保可追溯性
- 属性测试验证设计文档中定义的通用正确性属性
- 单元测试验证具体示例和边界情况
