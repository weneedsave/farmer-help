from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.category_service import get_category_map, get_category_stats

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("/")
def list_categories():
    """获取所有文档分类（中英文映射）"""
    return get_category_map()


@router.get("/stats")
def category_statistics(db: Session = Depends(get_db)):
    """获取每个分类下的文档数量统计"""
    return get_category_stats(db)
