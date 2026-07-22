import uvicorn
from fastapi import FastAPI

from database import create_tables
from routers import documents, chat, supplies, feedback, categories

app = FastAPI(title="农业AI助手", version="1.0.0")

# 启动时自动建表
create_tables()

# 挂载路由
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(supplies.router)
app.include_router(feedback.router)
app.include_router(categories.router)


@app.get("/")
def root():
    return {"message": "农业AI助手 API 已启动", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
