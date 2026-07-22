import os
import re
import aiofiles
import httpx
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from config import get_settings
from models import Document
from schemas import UploadResponse, URLUploadRequest, DocumentItem, DocumentListResponse, MessageBase


router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: str = "general",
    db: Session = Depends(get_db),
):
    """上传文档文件"""
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    safe_name = file.filename.replace("\\", "/").split("/")[-1]
    save_path = os.path.join(settings.upload_dir, safe_name)

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    ext = safe_name.lower().split(".")[-1] if "." in safe_name else "unknown"

    doc = Document(
        title=safe_name,
        source_type="file",
        source_path=save_path,
        file_type=ext,
        category=category,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 自动触发向量化入库
    from services.embedding_service import process_file
    try:
        process_file(save_path, doc.id, db)
        db.refresh(doc)
    except Exception:
        pass  # process_file 内部已设置 status="error"

    return UploadResponse(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        file_type=doc.file_type,
        category=doc.category,
        status=doc.status,
        chunk_count=doc.chunk_count,
        created_at=doc.created_at,
    )


@router.post("/upload-url", response_model=UploadResponse)
async def upload_url(
    body: URLUploadRequest,
    db: Session = Depends(get_db),
):
    """从网页链接抓取内容并保存"""
    settings = get_settings()

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(body.url)
            resp.raise_for_status()
            html_content = resp.text
    except httpx.HTTPError:
        raise HTTPException(status_code=400, detail=f"抓取网页失败，无法访问该链接")
    except Exception:
        raise HTTPException(status_code=400, detail="无法访问该链接，请检查URL")

    title = body.title or ""
    if not title:
        match = re.search(r"<title>(.+?)</title>", html_content, re.IGNORECASE)
        title = match.group(1).strip() if match else "未命名网页"

    os.makedirs(settings.upload_dir, exist_ok=True)
    safe_name = f"{title.replace('/', '_').replace('\\', '_')}.html"
    save_path = os.path.join(settings.upload_dir, safe_name)

    async with aiofiles.open(save_path, "w", encoding="utf-8") as f:
        await f.write(html_content)

    doc = Document(
        title=title,
        source_type="url",
        source_path=body.url,
        file_type="html",
        category="general",
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 自动触发向量化入库
    from services.embedding_service import process_file
    try:
        process_file(save_path, doc.id, db)
        db.refresh(doc)
    except Exception:
        pass  # process_file 内部已设置 status="error"

    return UploadResponse(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        file_type=doc.file_type,
        category=doc.category,
        status=doc.status,
        chunk_count=doc.chunk_count,
        created_at=doc.created_at,
    )


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    category: str = Query(default=None),
    status: str = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """文档列表（支持按分类/状态筛选 + 分页）"""
    q = db.query(Document)

    if category:
        q = q.filter(Document.category == category)
    if status:
        q = q.filter(Document.status == status)

    total = q.count()
    items = (
        q.order_by(Document.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return DocumentListResponse(
        total=total,
        items=[DocumentItem.model_validate(doc) for doc in items],
    )


@router.delete("/{doc_id}", response_model=MessageBase)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
):
    """删除文档及其向量数据"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 删除向量库中的切片
    from services.embedding_service import remove_document
    try:
        remove_document(doc_id)
    except Exception:
        pass  # 向量库可能已经清空，忽略

    # 删除磁盘文件（仅本地文件）
    if doc.source_type == "file" and os.path.exists(doc.source_path):
        try:
            os.remove(doc.source_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()

    return MessageBase(success=True, message=f"文档 '{doc.title}' 已删除")
