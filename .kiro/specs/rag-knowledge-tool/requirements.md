# 需求文档

## 简介

将 rag-agent 中基于 ChromaDB 的知识库检索能力封装为 LangChain `@tool`，替换 fastapi-agent 中硬编码的模拟知识库工具 `search_knowledge`。封装后的工具带有清晰的描述信息，使 Agent（基于 `create_react_agent`）能够根据用户问题自主判断是否需要查询本地文档知识库，与现有的 `get_current_time` 和 `calculate` 工具协同工作。

## 术语表

- **FastAPI_Agent**: 基于 FastAPI + LangChain 的 HTTP Agent 服务，位于 `fastapi-agent/` 目录
- **RAG_System**: 基于 ChromaDB 向量数据库和 OpenAI Embeddings 的检索增强生成系统，位于 `rag-agent/` 目录
- **Knowledge_Tool**: 封装了 RAG 检索能力的 LangChain @tool 工具，供 Agent 调用
- **ChromaDB**: 向量数据库，存储文档的向量化表示，用于语义相似度检索
- **Retriever**: LangChain 检索器，从 ChromaDB 中检索与查询语义最相关的文本块
- **Agent**: 基于 LangGraph `create_react_agent` 创建的 ReAct Agent 实例

## 需求

### 需求 1：Knowledge_Tool 工具定义

**用户故事：** 作为开发者，我希望知识库检索被封装为带有清晰描述的 LangChain @tool，以便 Agent 能理解该工具的用途并自主决定何时调用。

#### 验收标准

1. THE Knowledge_Tool SHALL 使用 LangChain 的 `@tool` 装饰器定义，接受一个 `query` 字符串参数
2. THE Knowledge_Tool SHALL 包含描述信息，明确说明该工具用于"从本地文档知识库中检索信息，适用于需要查找技术文档、教程、指南等知识性问题"
3. WHEN 用户提出知识性问题时，THE Agent SHALL 自主判断并调用 Knowledge_Tool 进行检索
4. WHEN 用户提出数学计算或时间查询等非知识性问题时，THE Agent SHALL 调用对应的 calculate 或 get_current_time 工具，而非 Knowledge_Tool

### 需求 2：RAG 检索集成

**用户故事：** 作为开发者，我希望 Knowledge_Tool 使用真正的 ChromaDB 向量检索替代硬编码字典，以便返回语义相关的文档内容。

#### 验收标准

1. THE Knowledge_Tool SHALL 使用 OpenAI Embeddings 将查询文本转为向量
2. THE Knowledge_Tool SHALL 从 ChromaDB 向量数据库中检索与查询语义最相关的文本块
3. THE Knowledge_Tool SHALL 返回检索到的文本内容，每个文本块之间使用分隔符分开
4. WHEN ChromaDB 中存在与查询相关的文档时，THE Knowledge_Tool SHALL 返回最多 3 个最相关的文本块
5. WHEN ChromaDB 中不存在与查询相关的文档时，THE Knowledge_Tool SHALL 返回提示信息说明未找到相关内容

### 需求 3：ChromaDB 连接配置

**用户故事：** 作为开发者，我希望 ChromaDB 的连接路径和 Embedding 模型通过环境变量配置，以便在不同环境中灵活部署。

#### 验收标准

1. THE Knowledge_Tool SHALL 从环境变量 `CHROMA_PATH` 读取 ChromaDB 数据存储路径
2. WHEN 环境变量 `CHROMA_PATH` 未设置时，THE Knowledge_Tool SHALL 使用默认路径 `../rag-agent/chroma_db`
3. THE Knowledge_Tool SHALL 从环境变量 `OPENAI_EMBEDDING_MODEL` 读取 Embedding 模型名称
4. WHEN 环境变量 `OPENAI_EMBEDDING_MODEL` 未设置时，THE Knowledge_Tool SHALL 使用默认值 `text-embedding-3-small`
5. THE Knowledge_Tool SHALL 复用环境变量 `OPENAI_API_KEY` 和可选的 `OPENAI_BASE_URL` 进行 API 认证

### 需求 4：错误处理

**用户故事：** 作为开发者，我希望 Knowledge_Tool 在异常情况下返回友好的错误信息，以便 Agent 能将错误信息传达给用户。

#### 验收标准

1. IF ChromaDB 数据库文件不存在，THEN THE Knowledge_Tool SHALL 返回错误信息提示用户先运行文档入库脚本
2. IF Embedding API 调用失败，THEN THE Knowledge_Tool SHALL 返回错误信息说明检索服务暂时不可用
3. IF 检索过程中发生未预期的异常，THEN THE Knowledge_Tool SHALL 捕获异常并返回包含错误描述的字符串，而非抛出异常

### 需求 5：依赖管理

**用户故事：** 作为开发者，我希望 fastapi-agent 的依赖文件包含 RAG 检索所需的新依赖，以便一次安装即可运行。

#### 验收标准

1. THE fastapi-agent 的 requirements.txt SHALL 包含 `chromadb` 依赖
2. THE fastapi-agent 的 requirements.txt SHALL 包含 `langchain-community` 依赖
3. THE fastapi-agent 的 requirements.txt SHALL 包含 `langchain-text-splitters` 依赖

### 需求 6：Agent 工具集成

**用户故事：** 作为开发者，我希望 Knowledge_Tool 与现有工具一起注册到 Agent 中，以便 Agent 拥有完整的工具集。

#### 验收标准

1. THE FastAPI_Agent 的 ALL_TOOLS 列表 SHALL 包含 Knowledge_Tool、get_current_time 和 calculate 三个工具
2. WHEN Agent 收到用户消息时，THE Agent SHALL 能够在一次对话中组合使用多个工具
3. THE Knowledge_Tool SHALL 替换原有的硬编码 search_knowledge 工具
