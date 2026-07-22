from database import get_chroma_collection
from services.embedding_service import  get_embeddings
import json
import time

#向量检索:把问题向量化,在ChromaDB中寻找相似文本
def retrieve(query_text:str,top_k:int=4) -> list[dict]:

    # 1,拿到embedding模型和chroma集合
    embeddings = get_embeddings()
    collection = get_chroma_collection()
    # 2.问题转化为向量
    query_vector = embeddings.embed_documents([query_text])[0]
    # 3.在ChromaDB中寻找相似文本
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents","metadatas","distances"],
    )

    # 4.整理成统一格式
    # results的值都是双层列表[[...]]，取[0]展开
    sources= []
    ids_list = results.get("ids",[[]])[0]
    docs_list = results.get("documents",[[]])[0]
    metas_list = results.get("metadatas",[[]])[0]
    dists_list = results.get("distances",[[]])[0]
    #余弦距离转相似度
    for i in range(len(ids_list)):
        # 如果metas_list有第i项，取出该批次所有文档的元数据数组；
        metadata = metas_list[i] if i<len(metas_list) else {}
        distance = dists_list[i] if i<len(dists_list) else 0
        score = round(1.0-distance,4)
        sources.append({
            "title": metadata.get("title","未知文档"),
            "content_snippet": docs_list[i] if i<len(docs_list) else "","score":score,
        })
    return sources

#把片段拼接成文本
def build_context(sources:list[dict]) -> str:
    if not sources:
        return "暂无资料"

    parts = []
    for i,src in enumerate(sources,start=1):
        title = src.get("title","未知文档")
        content=src.get("content_snippet","")
        parts.append(f"[来源{i}. {title}]\n{content}")

    return "\n".join(parts)

#取出对话历史
def get_conversation_history(conversation_id:str,db,limit:int=10)->str:
    # 1.从数据库中取出对话历史
    from models import Message
    messages = (
        db.query(Message)
        .filter(Message.conversation_id==conversation_id)
        .order_by(Message.id.desc())
        .all()

    )[::-1]#反转为正序

    if not messages:
        return ""
    lines = []
    for msg in messages:
        if msg.role=="user":
            lines.append(f"用户: {msg.content}")
        elif msg.role=="assistant":
            lines.append(f"rag: {msg.content}")
    return "\n".join(lines)


def query(query_text: str, conversation_id: str, db) -> dict:
      """完整 RAG 问答：检索 + 历史 + LLM + 保存消息 + 记录日志"""
      from models import Message, QueryLog
      from services.llm_service import get_llm
      # 1. 检索相关知识
      sources = retrieve(query_text, top_k=4)
      context = build_context(sources)
      # 2. 获取对话历史
      history = get_conversation_history(conversation_id, db,
      limit=10)
      # 3. 构建 System Prompt
      system_prompt = (
          "你是沃玛，一个活泼搞怪的农业技术助手，喜欢用颜文字和表情 (๑•̀ㅂ•́)و✧\n"
          "请基于以下参考资料回答用户问题。\n"
          "规则：\n"
          "1. 回答风格活泼搞怪，多使用颜文字或表情 (◕‿◕) ᕙ(⇀‸↼‶)ᕗ\n"
          "2. 如果资料中有答案，直接引用并注明来源编号\n"
          "3. 如果资料不包含答案，回答：'这个问题数据库中不存在请联系刘子旭及时添加相关资料'\n"
          "4. 用通俗易懂的语言，适合农民理解\n"
          "5. 涉及用量/配比时，务必提醒'请结合当地农技站建议'\n"
      )

      # 4. 拼接完整 Prompt
      full_prompt = f"{system_prompt}\n\n--- 参考资料---\n{context}\n\n--- 对话历史 ---\n{history}\n\n用户当前问题:{query_text}\n\n请回答:"
      # 5. 调用 LLM
      start_time = time.time()
      llm = get_llm()
      response = llm.invoke(full_prompt)
      answer = response.content
      elapsed_ms = int((time.time() - start_time) * 1000)
      # 6. 保存用户消息
      user_msg = Message(
          conversation_id=conversation_id,
          role="user",
          content=query_text,
      )
      db.add(user_msg)
      db.flush()  # 刷出 message_id，用于日志关联

      # 7. 保存 AI 回复
      ai_msg = Message(
          conversation_id=conversation_id,
          role="assistant",
          content=answer,
          sources=json.dumps(sources, ensure_ascii=False),
      )
      db.add(ai_msg)

      # 8. 记录检索日志
      log = QueryLog(
          query=query_text,
          hit_count=len(sources),
          response_time_ms=elapsed_ms,
      )
      db.add(log)
      db.commit()
      return {
          "conversation_id": conversation_id,
          "message_id": ai_msg.id,
          "answer": answer,
          "sources": sources,
      }