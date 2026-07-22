import json
from services.llm_service import get_llm
from services.rag_service import retrieve,build_context

#提取结构化信息
def _extract_supply_info(context:str,supply_type:str) -> list[dict]:
    if not context or context =="暂无资料":
        return []
    type_label  = "农药" if supply_type == "pesticide" else "化肥" if supply_type == "fertilizer" else "农资"

    prompt=(
          f"你是专业的{type_label}专家。请从以下资料中提取所有{type_label}信息。\n"
          f"对每个{type_label}，提取以下字段：\n"
          f"- name: {type_label}名称\n"
          f"- usage: 用法用量（没有则写'暂无'）\n"
          f"- precautions: 注意事项（没有则写'暂无'）\n\n"
          f"规则：\n"
          f"1. 只输出纯 JSON 数组，不要加 markdown 代码块标记\n"
          f"2. 如果资料中没有{type_label}信息，输出 []\n"
          f"3. 不要编造任何数据\n\n"
          f"--- 资料 ---\n{context}\n\n请输出 JSON 数组："
    )
    llm = get_llm()
    response = llm.invoke(prompt)
    text = response.content.strip()

    #清理可能的markdonw 标记
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:]) if lines[0].startswith("```") else text
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []

#拼接文本精确度
def search_supplies(keyword: str, supply_type:str = "pesticide", top_k: int = 5) -> dict:
    type_map={"pesticide":"农药","fertilizer":"化肥"}
    type_cn=type_map.get(supply_type,"农资")
    query_text = f"{keyword},{type_cn}"
    #检索
    sources = retrieve(query_text, top_k=top_k)
    #拼接上下文
    context = build_context(sources)

    #LLM提取结构化信息
    items = _extract_supply_info(context, supply_type)

    #给结果加上来源
    for item in items:
        if sources :
            item["source_title"] = sources[0].get("title", "未知文档")
    return {
        "keyword": keyword,
        "supply_type": supply_type,
        "results": items,
     }