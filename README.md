# 🌾 沃玛 — 农业AI助手

基于 RAG 的智能农业问答系统，面向农民提供种植技术、病虫害防治、农药化肥用法、农业政策等知识服务。

## 技术栈

| 层 | 选型 |
|---|------|
| LLM | DeepSeek V4-Flash |
| Embedding | BAAI/bge-small-zh-v1.5（本地离线） |
| 编排 | LangChain |
| 向量库 | ChromaDB |
| 关系库 | SQLite |
| 后端 | FastAPI |
| 界面 | Streamlit |

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件：

```
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. 启动后端

```bash
python main.py
```

### 4. 启动前端（新终端）

```bash
streamlit run app.py
```

访问 http://localhost:8501

## 项目结构

```
farmer_help/
├── main.py              # FastAPI 入口
├── app.py               # Streamlit 前端
├── config.py            # 配置管理
├── database.py          # 数据库连接
├── models.py            # ORM 模型
├── schemas.py           # Pydantic 请求/响应模型
├── services/
│   ├── llm_service.py         # DeepSeek LLM 调用
│   ├── embedding_service.py   # 文档加载/切片/向量化
│   ├── rag_service.py         # RAG 检索+问答
│   ├── supplies_service.py    # 农资检索
│   └── category_service.py    # 分类管理
├── routers/
│   ├── chat.py           # 对话接口
│   ├── documents.py      # 文档上传/管理
│   ├── supplies.py       # 农资检索接口
│   ├── feedback.py       # 反馈接口
│   └── categories.py     # 分类接口
└── images/               # 前端头像/背景图片
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 健康检查 |
| GET | `/documents/` | 文档列表（支持分类/状态筛选+分页） |
| POST | `/documents/upload` | 上传文档（自动向量化入库） |
| DELETE | `/documents/{id}` | 删除文档及向量数据 |
| POST | `/chat/new` | 新建对话 |
| POST | `/chat/send` | RAG 问答 |
| GET | `/chat/history/{id}` | 对话历史 |
| POST | `/supplies/search` | 农资检索（农药/化肥） |
| POST | `/feedback/` | 消息反馈 |
| GET | `/categories/` | 分类列表 |
| GET | `/categories/stats` | 分类文档统计 |
