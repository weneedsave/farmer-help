import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import get_settings

settings = get_settings()

#SQLlite
engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    connect_args={"check_same_thread": False}, #允许多线程
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db() -> Session:
    #给每个api独立获取数据库会话
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def create_tables():
    #在启动服务器时创建数据库表
    from models import Base
    Base.metadata.create_all(bind=engine)


#chromaDB设置
chroma_client =chromadb.PersistentClient(path=settings.chroma_persist_dir)

def get_chroma_collection(name: str = "agriculture_knowledge"):
    #获取chromaDB集合
    return chroma_client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
