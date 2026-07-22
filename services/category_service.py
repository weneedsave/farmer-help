from sqlalchemy import func
from models import Document

"""返回所有分类的中英文映射"""
def get_category_map() -> list[dict]:

    return [
        {"value": "general", "label": "通用"},
        {"value": "pest_disease", "label": "病虫害"},
        {"value": "pesticide", "label": "农药"},
        {"value": "fertilizer", "label": "化肥"},
        {"value": "planting", "label": "种植技术"},
        {"value": "soil", "label": "土壤"},
        {"value": "policy", "label": "农业政策"},
    ]

#查询每个分类的文档数量和分布

def get_category_stats(db) -> dict:
    rows = (
        db.query(
            Document.category,
            Document.status,
            func.count(Document.id).label("cnt"),
        )
        .group_by(Document.category, Document.status)
        .all()
    )
    #初始计数器
    categories = {}
    for cat in get_category_map():
        categories[cat["value"]] = {
            "label": cat["label"],
            "count": 0,
            "done": 0,
            "pending": 0,
            "processing": 0,
            "error": 0,
        }
    total=0
    for category, status, cnt in rows:
        if category in categories:
            categories[category][status] = cnt
            categories[category]["count"] += cnt
        total += cnt

    return {"total": total, "categories": categories}