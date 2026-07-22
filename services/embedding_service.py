#文档加载,切片,向量化

from langchain_community.document_loaders import TextLoader,PyPDFLoader,Docx2txtLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from database import  get_chroma_collection
from database import get_db

def load_document(file_path: str) -> list[Document]:
    ext = file_path.lower().split(".")[-1]
    #根据文件后缀不同选择不同的加载,返回一个列表
    if ext == "pdf":
        loader = PyPDFLoader(file_path)
    elif ext == "docx":
        loader = Docx2txtLoader(file_path)
    elif ext in ("txt","md"):
        loader = TextLoader(file_path,encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件格式:.{ext} (支持: .pdf, .docx, .txt, .md)")
    return loader.load()

#q切片
def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )
    return splitter.split_documents(docs)
#获取本地模型
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5",
        model_kwargs={"device": "cpu", "local_files_only": True},
        encode_kwargs={"normalize_embeddings":True},
    )

def index_documents(
        chunks: list[Document],
        doc_id: int,
        title: str="",
        category: str="general",
)-> int:
    #把切片向量化，并保存到chroma数据库中,返回存入数量
    if not chunks:
        return 0
    collection = get_chroma_collection()
    embeddings = get_embeddings()
    ids = []
    metadatas = []
    for i,chunk in enumerate(chunks):
        ids.append(f"doc_{doc_id}_chunk_{i}")
        metadatas.append({
            "doc_id":str(doc_id),
            "title":title,
            "category":category,
            "chunk_index":i,
            "source":chunk.metadata.get("source",""),
        })
    #把文本转成向量
    texts = [chunk.page_content for chunk in chunks]
    vectors = embeddings.embed_documents(texts)

    collection.add(

        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,

    )
    return len(chunks)
def remove_document(doc_id: int)-> int:
    #删除切片
    #先获取id前缀为doc_id的向量
    collection = get_chroma_collection()
    results=collection.get(
        where={"doc_id":str(doc_id)},
    )
    ids_to_delete = results.get("ids",[])
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)

#完整入库流程-加载-切片-向量化-入库

def process_file(file_path:str,doc_id:int,db)-> int:
    from models import Document

    doc_record=db.query(Document).filter(Document.id==doc_id).first()
    if not doc_record:
        raise ValueError(f"文档记录不存在:id={doc_id}")

    try:
        #1,标记处理中
        doc_record.status="processing"
        db.commit()
        #2,加载文件
        docs = load_document(file_path)
        #3,切片
        chunks = split_documents(docs)
        #4,向量化入库
        count = index_documents(
            chunks,
            doc_id=doc_id,
            title=doc_record.title,
            category=doc_record.category,
        )
        # 5,更新数据库记录
        doc_record.chunk_count = count
        doc_record.status = "done"
        db.commit()

        return  count
    except Exception as e:
        doc_record.status = "error"
        db.commit()
        raise  e