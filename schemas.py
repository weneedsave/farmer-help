#step 5
from datetime import datetime
from typing import Optional,List
# fastapi的接口校验核心两个BaseModel,Field
from pydantic import BaseModel,Field


#通用

class MessageBase(BaseModel):
    """统一的成功/失败响应"""
    #... 代表必填项，接口返回时必须给 true / false，不能省略。
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="附加信息")
#文档上传
class URLUploadRequest(BaseModel):
    """提交链接抓取"""
    url: str = Field(..., description="要抓取的网页链接")
    title: Optional[str] = Field(default=None, description="手动指定标题，不填则自动提取")

class UploadResponse(BaseModel):
    #UploadResponse 是文件上传 / 网页链接抓取接口的返回数据模型，后端处理完上传后，把文档信息封装成这个结构返回给前端
    #文件上传/URL抓取的返回
    id: int = Field(..., description="文件ID")
    title:str
    source_type: str = Field(..., description="file或url")
    file_type:str
    category: str
    status: str = Field(..., description="pending/processing/done/error")
    chunk_count: int=0
    created_at:str
# 文档管理
class DocumentItem(BaseModel):
    #文档列表单条数据返回模型。
    # 查询全部文档时，列表里每一条数据都遵循这个结构；
    #文档列表
    id: int
    title: str
    source_type: str
    source_path: str
    file_type: str
    category: str
    chunk_count: int
    status: str
    created_at: str
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    total: int = Field(..., description="文档总数")
    items:List[DocumentItem]=Field(default_factory=list, description="文档列表")


#文档列表查询筛选
#文档列表查询接口的筛选参数模型，一般放在接口 Query 查询参数里，前端通过 URL 传参筛选文档：按分类、状态过滤，同时控制分页页码、每页条数
class DocumentFilter(BaseModel):
    category:Optional[str]=Field(default=None, description="文档所属农业类目:pest_disease/pesticide/fertilizer/planting/soil/policy/general")
    status:Optional[str]=Field(default=None, description="文档状态:pending/processing/done/error")
    page:int=Field(default=1,ge=1,le=100, description="页码")
    page_size:int=Field(default=20,ge=1,le=100, description="每页条数")


#对话

#新建对话返回,规定新建对话后，后端必须返回这 3 个字段
class ChatNewResponse(BaseModel):
    conversation_id: str=Field(...,description="新会话ID(uuid)")
    title:str=Field(default="新会话",description="会话标题")
    created_at:str

#发送数据
class ChatRequest(BaseModel):
    conversation_id: str=Field(...,description="会话ID(uuid)")
    message: str=Field(...,min_length=1,max_length=5000,description="用户输入")

#RAG引用的知识来源
class SourceItem(BaseModel):
    title: str=Field(...,description="文档标题")
    content_snippet: str=Field(default="",description="匹配到的文档片段")
    score:Optional[float] = Field(default=None,description="相似度得分")

#回复
class ChatResponse(BaseModel):
    conversation_id: str
    message_id:int=Field(...,description="本条消息ID")
    answer:str=Field(...,description="回复内容")
    sources: List[SourceItem]=Field(default_factory=list,description="知识来源")

# 历史消息条目
#聊天历史单条消息的返回模型，接口查询对话历史时，数组里每一条消息都遵循这个结构
class MessageItem(BaseModel):
    id:int
    role: str=Field(...,description="user或assistant")
    content:str
    sources:Optional[str] = Field(default=None,description="JSON格式的来源引用")
    created_at:str
    class Config:
        from_attributes = True

#对话历史
class ChatHistoryResponse(BaseModel):
    conversation_id: str
    title: str
    messages: List[MessageItem]=Field(default_factory=list)


#农资检索
#农资检索请求
class SupplySearchRequest(BaseModel):
    keyword: str=Field(...,min_length=1,max_length=200,description="搜索的关键词")
    supply_type: str=Field(default="pesticide",description="农资类型")


#单条农资检索结果
class SupplyResult(BaseModel):
    name: str=Field(...,description="农资名称")
    usage: str=Field(default="",description="用法用量")
    precautions: str=Field(default="",description="注意事项")
    source_title: str=Field(default="",description="来源文档")

#农资检索响应
class SupplySearchResponse(BaseModel):
    keyword: str
    supply_type: str
    results: List[SupplyResult]=Field(default_factory= list)#传入函数



#反馈
#提交反馈
class FeedbackRequest(BaseModel):
    message_id: int=Field(...,description="消息ID")
    rating: str=Field(...,description="有帮助或无帮助")
    comment: Optional[str]=Field(default=None,max_length=500,description="补充描述(可选)")

#反馈提交结果
class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    rating: str
    comment: Optional[str]=None
    created_at: str


#病虫害诊断(第二期预留)
#发送请求
class DiagnosisRequest(BaseModel):
    description: str=Field(...,min_length=5,max_length=2000,description="描述作物症状")
    crop_type:Optional[str]=Field(default=None,description="作物类型")
    image_base64: Optional[str]=Field(default=None,description="图片base64编码")

#诊断结果
class DiagnosisResult(BaseModel):
    possible_disease: str=Field(...,description="可能患有的病")
    confidence: str=Field(...,description="置信度")
    symptoms_match:Optional[str] = Field(default=None,description="症状匹配")
    treatment: str=Field(default="",description="治疗建议")
    prevention: str=Field(default="",description="预防措施")

#诊断返回
class DiagnosisResponse(BaseModel):
    description:str
    results:List[DiagnosisResult]=Field(default_factory= list)