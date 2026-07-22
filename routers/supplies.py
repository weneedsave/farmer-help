from fastapi import APIRouter, Depends

from services.supplies_service import search_supplies as do_search
from schemas import SupplySearchRequest, SupplySearchResponse, SupplyResult

router = APIRouter(prefix="/supplies", tags=["农资检索"])


@router.post("/search", response_model=SupplySearchResponse)
def search_supplies(body: SupplySearchRequest):
    """农资检索（农药/化肥用法用量等）"""
    result = do_search(body.keyword, body.supply_type)

    items = [
        SupplyResult(
            name=item.get("name", ""),
            usage=item.get("usage", "暂无"),
            precautions=item.get("precautions", "暂无"),
            source_title=item.get("source_title", "未知文档"),
        )
        for item in result["results"]
    ]

    return SupplySearchResponse(
        keyword=result["keyword"],
        supply_type=result["supply_type"],
        results=items,
    )
