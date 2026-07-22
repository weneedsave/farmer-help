import os
import glob
import base64
import streamlit as st
import requests

# ============================================================
# 🎨 自定义配置区 —— 改这里就行
# ============================================================
AI_NAME = "沃玛"
AI_EMOJI = "🌾"
USER_EMOJI = "👨‍🌾"
PAGE_TITLE = f"{AI_EMOJI} {AI_NAME} — 农业AI助手"

# 图片路径：支持 png / jpg / jpeg / gif / webp，找到第一个匹配的就用
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")

def _find_image(prefix):
    """在 images/ 下找 prefix.* 的第一张图片，找不到返回 None"""
    for ext in ("png", "jpg", "jpeg", "gif", "webp"):
        path = os.path.join(IMG_DIR, f"{prefix}.{ext}")
        if os.path.exists(path):
            return path
    return None

AI_AVATAR_FINAL = _find_image("ai_avatar") or AI_EMOJI
USER_AVATAR_FINAL = _find_image("user_avatar") or USER_EMOJI
LOGO_PATH = _find_image("logo")
BG_PATH = _find_image("background")


def _img_to_base64(path):
    """把图片文件转成 base64 data URI，用于 CSS 背景"""
    if not path:
        return None
    ext = path.lower().split(".")[-1]
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"

# ============================================================
# 🎨 自定义 CSS —— 阳光田园风
# ============================================================
def inject_css():
    bg_css = ""
    bg_b64 = _img_to_base64(BG_PATH)
    if bg_b64:
        bg_css = f"""
        .stApp {{
            background: linear-gradient(rgba(255,255,255,0.35), rgba(255,255,255,0.35)),
                        url("{bg_b64}") center/cover fixed;
        }}
        """
    else:
        bg_css = """
        .stApp {
            background: linear-gradient(180deg, #fef9e7 0%, #fefce8 30%, #f7fee7 60%, #ecfccb 100%);
        }
        """

    st.markdown(f"""
    <style>
    /* ========== 全局背景 ========== */
    {bg_css}

    /* ========== 主色调覆盖 ========== */
    :root {{
        --primary: #65a30d;
        --primary-light: #84cc16;
        --gold: #f59e0b;
        --warm-bg: #fffbeb;
    }}

    /* ========== 侧边栏 ========== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #fef3c7 0%, #fef9e7 50%, #f7fee7 100%);
        border-right: 2px solid #d9f99d;
    }}
    [data-testid="stSidebar"] h1 {{
        color: #4d7c0f !important;
    }}

    /* ========== 主标题 ========== */
    .main-title {{
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #65a30d, #84cc16, #a3e635);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}

    /* ========== 卡片样式 ========== */
    .stContainer {{
        border: 1px solid #d9f99d !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #fffbeb, #f7fee7) !important;
        box-shadow: 0 2px 8px rgba(101, 163, 13, 0.08) !important;
        transition: box-shadow 0.2s;
    }}
    .stContainer:hover {{
        box-shadow: 0 4px 16px rgba(101, 163, 13, 0.15) !important;
    }}

    /* ========== 主内容区域 ========== */
    .main .block-container {{
        background: rgba(255,255,255,0.6);
        border-radius: 16px;
        padding: 2rem !important;
    }}

    /* ========== 聊天消息 ========== */
    [data-testid="stChatMessage"] {{
        border-radius: 16px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        color: #1a1a1a !important;
    }}
    [data-testid="stChatMessage"] * {{
        color: #1a1a1a !important;
    }}
    /* 代码块保持深色背景 */
    [data-testid="stChatMessage"] code {{
        background: #f0f0f0 !important;
        color: #d63384 !important;
    }}

    /* ========== 按钮 ========== */
    .stButton > button {{
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(101, 163, 13, 0.25) !important;
    }}

    /* 新建对话按钮 */
    div[data-testid="stSidebar"] .stButton:first-of-type > button {{
        background: linear-gradient(135deg, #65a30d, #84cc16) !important;
        color: white !important;
    }}

    /* ========== 输入框 ========== */
    [data-testid="stChatInput"] textarea {{
        border: 2px solid #d9f99d !important;
        border-radius: 12px !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border-color: #84cc16 !important;
        box-shadow: 0 0 0 3px rgba(132, 204, 22, 0.15) !important;
    }}

    /* ========== Metric 数字 ========== */
    [data-testid="stMetricValue"] {{
        color: #65a30d !important;
        font-weight: 800 !important;
    }}

    /* ========== 展开面板 ========== */
    .streamlit-expanderHeader {{
        background: #f7fee7 !important;
        border-radius: 8px !important;
    }}

    /* ========== 滚动条 ========== */
    ::-webkit-scrollbar-track {{ background: #fef9e7; }}
    ::-webkit-scrollbar-thumb {{ background: #a3e635; border-radius: 8px; }}

    /* ========== 底部信息 ========== */
    .footer {{
        text-align: center;
        color: #84cc16;
        font-size: 0.85rem;
        margin-top: 1rem;
        opacity: 0.7;
    }}
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 页面配置
# ============================================================
st.set_page_config(page_title=PAGE_TITLE, page_icon=AI_EMOJI, layout="wide")
inject_css()

API = "http://localhost:8000"


# ============================================================
# 工具函数
# ============================================================
def show_logo():
    """顶部 Logo + 标题"""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if LOGO_PATH:
            st.image(LOGO_PATH, width=80)
        st.markdown(f'<div class="main-title">{PAGE_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center;color:#84cc16;margin-bottom:1.5rem;">'
            '🌱 选种 · 施肥 · 病虫害 · 农药用法 · 政策查询 🌱</p>',
            unsafe_allow_html=True,
        )


# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    if LOGO_PATH:
        st.image(LOGO_PATH, width=60)
    st.title(f"{AI_EMOJI} {AI_NAME}")

    st.markdown(f"你好！我是**{AI_NAME}**，你的专属农业助手 🧑‍🌾")

    if st.button(f"➕ 新建对话", use_container_width=True):
        try:
            r = requests.post(f"{API}/chat/new")
            if r.ok:
                data = r.json()
                st.session_state.conv_id = data["conversation_id"]
                st.session_state.messages = []
                st.rerun()
        except Exception:
            st.error("后端服务未启动")

    st.divider()
    st.markdown("### 📋 功能区")

    if st.button("📄 知识库文档", use_container_width=True):
        st.session_state.page = "docs"
        st.rerun()
    if st.button("🔍 农资检索", use_container_width=True):
        st.session_state.page = "supplies"
        st.rerun()
    if st.button("💬 回到对话", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()

    st.divider()
    st.markdown(
        f'<p style="font-size:0.8rem;color:#65a30d;">'
        f'👨‍🌾 用户头像 → images/user_avatar.png<br>'
        f'🌾 AI头像 → images/ai_avatar.png<br>'
        f'🖼️ 背景 → images/background.png'
        f'</p>',
        unsafe_allow_html=True,
    )

# ============================================================
# Init session state
# ============================================================
for key, default in [
    ("conv_id", None),
    ("messages", []),
    ("page", "chat"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================================
# 💬 对话页面
# ============================================================
if st.session_state.page == "chat":
    show_logo()

    # 自动创建对话
    if st.session_state.conv_id is None:
        try:
            r = requests.post(f"{API}/chat/new")
            if r.ok:
                st.session_state.conv_id = r.json()["conversation_id"]
        except Exception:
            st.warning("⚠️ 请先启动后端服务: python main.py")

    if st.session_state.conv_id:
        st.caption(f"📝 会话: {st.session_state.conv_id[:8]}...")

    # 显示聊天记录
    for msg in st.session_state.messages:
        avatar = AI_AVATAR_FINAL if msg["role"] == "assistant" else USER_AVATAR_FINAL
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📖 参考来源"):
                    for src in msg["sources"]:
                        st.caption(f"📄 **{src.get('title', '未知')}** (匹配度: {src.get('score', 'N/A')})")
                        st.text(src.get("content_snippet", "")[:200])

    # 用户输入
    if prompt := st.chat_input(f"输入你的农业问题，{AI_NAME}为你解答..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR_FINAL):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AI_AVATAR_FINAL):
            with st.spinner(f"{AI_NAME} 正在思考..."):
                try:
                    r = requests.post(f"{API}/chat/send", json={
                        "conversation_id": st.session_state.conv_id,
                        "message": prompt,
                    })
                    if r.ok:
                        data = r.json()
                        answer = data["answer"]
                        sources = data["sources"]
                        st.markdown(answer)
                        if sources:
                            with st.expander("📖 参考来源"):
                                for src in sources:
                                    st.caption(f"📄 **{src.get('title', '未知')}** (匹配度: {src.get('score', 'N/A')})")
                                    st.text(src.get("content_snippet", "")[:200])
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "message_id": data["message_id"],
                        })
                    else:
                        st.error(f"请求失败: {r.status_code}")
                except Exception as e:
                    st.error(f"连接失败: {e}")

    st.markdown('<div class="footer">🌾 用科技助力农业 · 让知识服务田间 🌾</div>', unsafe_allow_html=True)


# ============================================================
# 📄 知识库页面
# ============================================================
elif st.session_state.page == "docs":
    show_logo()

    try:
        r = requests.get(f"{API}/documents/")
        if r.ok:
            data = r.json()

            col1, col2, col3, col4 = st.columns(4)
            total = data["total"]
            done_count = sum(1 for d in data["items"] if d["status"] == "done")
            with col1:
                st.metric("📚 文档总数", total)
            with col2:
                st.metric("✅ 已入库", done_count)
            with col3:
                st.metric("📦 分类数", len(set(d["category"] for d in data["items"])))

            st.divider()

            for doc in data["items"]:
                status_map = {
                    "done": ("✅", "已入库"),
                    "pending": ("⏳", "待处理"),
                    "processing": ("🔄", "处理中"),
                    "error": ("❌", "失败"),
                }
                icon, label = status_map.get(doc["status"], ("❓", doc["status"]))

                cat_map = {
                    "general": "通用", "pest_disease": "病虫害", "pesticide": "农药",
                    "fertilizer": "化肥", "planting": "种植技术", "soil": "土壤", "policy": "农业政策",
                }
                cat_label = cat_map.get(doc["category"], doc["category"])

                with st.container(border=True):
                    cols = st.columns([4, 1, 1])
                    cols[0].markdown(f"**{doc['title']}**")
                    cols[1].caption(f"{icon} {label}")
                    cols[2].caption(f"📦 {doc['chunk_count']}块")
                    st.caption(f"📁 {doc['file_type']} | 🏷️ {cat_label} | 🕐 {doc['created_at']}")

        # 上传
        st.divider()
        st.subheader("📤 上传新文档")
        col_a, col_b = st.columns([3, 1])
        with col_a:
            uploaded = st.file_uploader(
                "选择文件 (pdf / txt / md / docx)",
                type=["pdf", "txt", "md", "docx"],
                label_visibility="collapsed",
            )
        with col_b:
            cat = st.selectbox(
                "分类",
                ["general", "pest_disease", "pesticide", "fertilizer", "planting", "soil", "policy"],
                format_func=lambda x: {
                    "general": "通用", "pest_disease": "病虫害", "pesticide": "农药",
                    "fertilizer": "化肥", "planting": "种植技术", "soil": "土壤", "policy": "政策",
                }.get(x, x),
            )

        if uploaded and st.button("🚀 上传到知识库", use_container_width=True):
            with st.spinner("上传中..."):
                r = requests.post(
                    f"{API}/documents/upload",
                    files={"file": (uploaded.name, uploaded.getvalue())},
                    params={"category": cat},
                )
                if r.ok:
                    st.success(f"✅ {uploaded.name} 上传成功！")
                    st.rerun()
                else:
                    st.error(f"上传失败: {r.text}")
    except Exception:
        st.warning("⚠️ 请先启动后端服务: python main.py")


# ============================================================
# 🔍 农资检索页面
# ============================================================
elif st.session_state.page == "supplies":
    show_logo()

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        keyword = st.text_input("🔍 搜索关键词", placeholder="如：稻瘟灵、复合肥、杀虫剂...", label_visibility="collapsed")
    with col2:
        stype = st.selectbox("类型", ["pesticide", "fertilizer"], format_func=lambda x: "农药" if x == "pesticide" else "化肥")
    with col3:
        search_btn = st.button("🔍 搜索", use_container_width=True)

    if search_btn and keyword:
        with st.spinner("检索中..."):
            try:
                r = requests.post(f"{API}/supplies/search", json={
                    "keyword": keyword,
                    "supply_type": stype,
                })
                if r.ok:
                    data = r.json()
                    if data["results"]:
                        st.success(f"找到 {len(data['results'])} 条结果")
                        for item in data["results"]:
                            with st.container(border=True):
                                st.subheader(f"📦 {item['name']}")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.markdown(f"**💊 用法用量**\n{item['usage']}")
                                with col_b:
                                    st.markdown(f"**⚠️ 注意事项**\n{item['precautions']}")
                                st.caption(f"📄 来源: {item.get('source_title', '未知文档')}")
                    else:
                        st.info(f"未找到关于「{keyword}」的农资信息，建议上传相关文档到知识库")
                else:
                    st.error("检索失败")
            except Exception:
                st.warning("⚠️ 请先启动后端服务: python main.py")
