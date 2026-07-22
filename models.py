#五张表的Python映射
import uuid
from datetime import datetime

from sqlalchemy import Column,Integer,String,Text,Float,ForeignKey
from sqlalchemy.orm import DeclarativeBase,relationship
#DeclarativeBase是SQLAlchemy的基类
#relationship代码层便捷联表查询
#Column 是用来定义数据表的一列
class Base(DeclarativeBase):
    #所有模型的基类
    pass
def _new_uuid() -> str:
    return str(uuid.uuid4())
#获取当前本地时间，并格式化为 年-月-日 时:分:秒 的字符串，用于存入数据库、返回接口时间。
def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#文档表
class Document(Base):
    __tablename__ = "documents"
    #id字段,int,自增,主键
    id=Column(Integer,primary_key=True,autoincrement=True)
    title = Column(String(200),nullable=False,comment="文档标题")
    #资源类型:非空,用来区分当前资源是本地文件，还是网络链接
    source_type =Column(String(500),nullable=False,comment="file或url")
    #资源路径:非空,用来存储当前资源的路径
    source_path=Column(String(500),nullable=False,comment="文件路径或url路径")
    #file_type 判断文件格式；category 区分文档所属农业类目，做分类筛选、分页查询。
    file_type=Column(String(10),nullable=False,comment="pdf/txt/md/docx")
    category=Column(String(30),default="general",comment="pest_disease/pesticide/fertilizer/planting/soil/policy/general")
    #切块,方便检索
    chunk_count = Column(Integer,default=0,comment="切分多少块")
    #status 任务处理状态,默认pending,一共5种
    status = Column(String(20),default="pending",comment="pending/processing/done/error")
    created_at = Column(String(20),default=_now)

#对话表
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(36),primary_key=True,default=_new_uuid)
    title=Column(String(200),nullable=False,comment="新对话")
    #查看文档是什么时候上传入库的；
    created_at = Column(String(20),default=_now)
    #修改文档的时候
    updated_at = Column(String(20),default=_now)


    #一对多:一个对话有多条消息
    #这行代码就是给会话加一个 .messages 属性，一点就能查出这场对话全部聊天记录，并且自动按发送顺序排好。
    #根据会话id查出所有消息
    messages = relationship("Message",back_populates="conversation",order_by="Message.id")
#消息表
class Message(Base):
    __tablename__ = "messages"

    id=Column(Integer,primary_key=True,autoincrement=True)
    conversation_id = Column(String(36),ForeignKey("conversations.id"),nullable=False,comment="关联会话id")
    role=Column(String(10),nullable=False,comment="系统/用户")
    content=Column(Text,nullable=False,comment="消息内容")
    sources=Column(Text,nullable=True,comment="消息来源格式为json字符串")
    created_at = Column(String(20),default=_now)

    #反向关系
    #单拿一条消息，可以直接查到它所属的整个会话
    conversation=relationship("Conversation",back_populates="messages")
#反馈表
class Feedback(Base):
    __tablename__ = "feedback"
    id=Column(Integer,primary_key=True,autoincrement=True)
    #关联消息
    message_id=Column(Integer,ForeignKey("messages.id"),nullable=False,comment="关联消息id")
    rating=Column(String(20),nullable=False,comment="有帮助/无帮助")
    comment = Column(Text,nullable=True,comment="反馈内容")
    created_at = Column(String(20),default=_now)
#检索日志表
class QueryLog(Base):
    __tablename__ = "query_log"

    id=Column(Integer,primary_key=True,autoincrement=True)
    query=Column(Text,nullable=False,comment="检索内容")
    hit_count=Column(Integer,default=0,comment="命中切片数量")
    response_time_ms=Column(Integer,default=0,comment="响应时间")
    created_at = Column(String(20),default=_now)
