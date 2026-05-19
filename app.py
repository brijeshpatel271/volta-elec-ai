"""
app.py — VOLTA Phase 2: Industrial Futuristic UI
"""
import streamlit as st
from utils.ollama_client import check_ollama_running, get_available_models, stream_chat, RECOMMENDED_MODELS
from utils.code_executor import execute_code, extract_code_blocks
from utils.session import init_session, add_message, get_messages_for_api, clear_history, export_chat_markdown, EXAMPLE_PROMPTS
from prompts.system_prompt import SYSTEM_PROMPT

try:
    from rag.retriever import build_rag_system_prompt, get_cited_sources
    from rag.ingestor import get_store_stats
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

st.set_page_config(
    page_title="VOLTA — Engineering AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session(st)
for k, v in [("theme", "dark"), ("rag_enabled", RAG_AVAILABLE), ("last_citations", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

DARK = st.session_state.theme == "dark"

# ── COLOR SYSTEM ─────────────────────────────
if DARK:
    BG       = "#080C10"
    BG2      = "#0D1318"
    PANEL    = "#111820"
    BORDER   = "#1E2D3D"
    BORDER2  = "#243444"
    TEXT     = "#C8D8E8"
    MUTED    = "#4A6070"
    ACCENT   = "#00D4FF"
    ACCENT2  = "#0098CC"
    GOLD     = "#FFB800"
    GREEN    = "#00FF88"
    RED      = "#FF3860"
    CODE_BG  = "#060A0E"
    USER_BG  = "#0A1A2E"
    USER_BR  = "#1E3A5F"
    BOT_BG   = "#0A1A12"
    BOT_BR   = "#1E3D2A"
else:
    BG       = "#F0F4F8"
    BG2      = "#E8EDF3"
    PANEL    = "#FFFFFF"
    BORDER   = "#C8D4E0"
    BORDER2  = "#B0BEC8"
    TEXT     = "#1A2530"
    MUTED    = "#7A9AAA"
    ACCENT   = "#0070CC"
    ACCENT2  = "#005499"
    GOLD     = "#CC8800"
    GREEN    = "#007744"
    RED      = "#CC2040"
    CODE_BG  = "#F8FAFC"
    USER_BG  = "#EBF4FF"
    USER_BR  = "#B8D4F0"
    BOT_BG   = "#EBFAF2"
    BOT_BR   = "#B8E8D0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

.stApp {{
    background: {BG} !important;
    font-family: 'Syne', sans-serif !important;
    color: {TEXT} !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -20%, {ACCENT}08 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, {GOLD}05 0%, transparent 50%);
    min-height: 100vh;
}}

[data-testid="stSidebar"] {{
    background: {BG2} !important;
    border-right: 1px solid {BORDER} !important;
    background-image: linear-gradient(180deg, {ACCENT}06 0%, transparent 40%) !important;
}}
[data-testid="stSidebar"] > div:first-child {{ padding-top: 0 !important; }}

#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER2}; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT}66; }}

[data-testid="stChatInputContainer"] {{
    background: {PANEL} !important;
    border-top: 1px solid {BORDER} !important;
    padding: 14px 20px !important;
}}
[data-testid="stChatInputContainer"] textarea {{
    background: {BG2} !important;
    border: 1px solid {BORDER2} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    padding: 11px 16px !important;
    transition: all 0.2s !important;
}}
[data-testid="stChatInputContainer"] textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px {ACCENT}22, 0 0 20px {ACCENT}11 !important;
    outline: none !important;
}}

.stButton button {{
    background: transparent !important;
    border: 1px solid {BORDER2} !important;
    color: {TEXT} !important;
    border-radius: 6px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    padding: 7px 14px !important;
    transition: all 0.15s !important;
}}
.stButton button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
    box-shadow: 0 0 12px {ACCENT}33 !important;
}}

[data-testid="stSelectbox"] > div > div {{
    background: {BG2} !important;
    border: 1px solid {BORDER2} !important;
    border-radius: 6px !important;
    color: {TEXT} !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
}}

code, pre {{
    font-family: 'IBM Plex Mono', monospace !important;
    background: {CODE_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-size: 12.5px !important;
}}

[data-testid="stExpander"] {{
    background: {BG2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
}}

hr {{ border-color: {BORDER} !important; margin: 10px 0 !important; opacity: 0.8 !important; }}
[data-testid="stChatMessage"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}
[data-testid="stSpinner"] p {{ font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; color: {MUTED} !important; }}
[data-testid="stAlert"] {{ border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-size: 13px !important; }}

/* CUSTOM COMPONENTS */
.v-sidebar-header {{
    background: linear-gradient(180deg, {BG} 0%, {BG2} 100%);
    border-bottom: 1px solid {BORDER};
    padding: 20px 18px 16px;
    position: relative;
    overflow: hidden;
}}
.v-sidebar-header::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {ACCENT}66, transparent);
}}
.v-wordmark {{
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 6px;
    color: {ACCENT};
    text-shadow: 0 0 20px {ACCENT}66;
    line-height: 1;
}}
.v-tagline {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    color: {MUTED};
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}}
.v-sec-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 2.5px;
    padding: 10px 0 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.v-sec-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {BORDER};
}}
.v-status {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
}}
.v-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.v-dot-green {{ background: {GREEN}; box-shadow: 0 0 6px {GREEN}88; animation: blink 2s infinite; }}
.v-dot-red   {{ background: {RED}; }}
.v-dot-yellow{{ background: {GOLD}; }}
@keyframes blink {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:0.4 }} }}
.v-domain-tag {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: {MUTED};
    margin: 2px 2px 0 0;
}}
.v-topbar {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 4px 14px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 24px;
    position: relative;
}}
.v-topbar::after {{
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 120px;
    height: 1px;
    background: {ACCENT};
    box-shadow: 0 0 8px {ACCENT}88;
}}
.v-title {{ flex: 1; }}
.v-title h1 {{
    font-family: 'Space Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 4px;
    color: {ACCENT};
    text-shadow: 0 0 15px {ACCENT}44;
    margin: 0; line-height: 1.2;
}}
.v-title p {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: {MUTED};
    letter-spacing: 1.5px;
    margin: 3px 0 0;
    text-transform: uppercase;
}}
.v-badge {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid;
}}
.v-badge-accent {{ color: {ACCENT}; border-color: {ACCENT}55; background: {ACCENT}11; }}
.v-badge-green  {{ color: {GREEN}; border-color: {GREEN}55; background: {GREEN}11; }}
.v-capgrid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin-bottom: 28px;
}}
.v-capcard {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 14px 10px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
}}
.v-capcard::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {ACCENT}, {GOLD});
    opacity: 0;
    transition: opacity 0.2s;
}}
.v-capcard:hover {{ border-color: {ACCENT}66; box-shadow: 0 4px 20px {ACCENT}11; }}
.v-capcard:hover::before {{ opacity: 1; }}
.v-capcard-icon {{ font-size: 22px; margin-bottom: 6px; }}
.v-capcard-title {{
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {TEXT};
    margin-bottom: 4px;
}}
.v-capcard-desc {{
    font-size: 10px;
    color: {MUTED};
    line-height: 1.4;
    font-family: 'IBM Plex Mono', monospace;
}}
.v-excard {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 14px;
    height: 100%;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}}
.v-excard::after {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: {ACCENT};
    opacity: 0;
    transition: opacity 0.2s;
}}
.v-excard:hover {{ border-color: {ACCENT}55; }}
.v-excard:hover::after {{ opacity: 1; }}
.v-exdom {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {ACCENT};
    margin-bottom: 6px;
}}
.v-extxt {{
    font-size: 12.5px;
    color: {TEXT};
    line-height: 1.5;
    font-family: 'Syne', sans-serif;
}}
.v-user-wrap {{
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 10px;
    margin: 12px 0;
}}
.v-user-msg {{
    background: {USER_BG};
    border: 1px solid {USER_BR};
    border-radius: 12px 4px 12px 12px;
    padding: 12px 16px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.6;
    color: {TEXT};
    font-family: 'Syne', sans-serif;
}}
.v-user-av {{
    width: 32px; height: 32px;
    background: {ACCENT2};
    border: 1px solid {ACCENT}55;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 2px;
    box-shadow: 0 0 10px {ACCENT}22;
}}
.v-bot-av {{
    width: 32px; height: 32px;
    background: linear-gradient(135deg, {ACCENT2}, {ACCENT});
    border: 1px solid {ACCENT}55;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 2px;
    box-shadow: 0 0 14px {ACCENT}33;
}}
.v-citebox {{
    background: {BG2};
    border: 1px solid {BORDER};
    border-left: 2px solid {ACCENT};
    border-radius: 0 6px 6px 0;
    padding: 8px 12px;
    margin: 4px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
}}
.v-citetit {{ color: {ACCENT}; font-weight: 500; }}
.v-citedom {{ color: {MUTED}; font-size: 10px; margin-top: 2px; }}
.v-execout {{
    background: {CODE_BG};
    border: 1px solid {GREEN}44;
    border-left: 2px solid {GREEN};
    border-radius: 0 6px 6px 0;
    padding: 12px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: {TEXT};
    white-space: pre-wrap;
    margin-top: 8px;
}}
.v-execerr {{
    background: {CODE_BG};
    border: 1px solid {RED}44;
    border-left: 2px solid {RED};
    border-radius: 0 6px 6px 0;
    padding: 12px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: {RED};
    white-space: pre-wrap;
    margin-top: 8px;
}}
.v-grid-bg {{
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient({BORDER}22 1px, transparent 1px),
        linear-gradient(90deg, {BORDER}22 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
    opacity: {'0.5' if DARK else '0.3'};
}}
.v-scan-line {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {ACCENT}88, transparent);
    animation: scan 8s linear infinite;
    pointer-events: none;
    z-index: 9998;
}}
@keyframes scan {{
    0%   {{ top: 0%; opacity: 0; }}
    5%   {{ opacity: 1; }}
    95%  {{ opacity: 1; }}
    100% {{ top: 100%; opacity: 0; }}
}}
</style>

<div class="v-grid-bg"></div>
<div class="v-scan-line"></div>
""", unsafe_allow_html=True)


# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="v-sidebar-header">
        <div class="v-wordmark">VOLTA</div>
        <div class="v-tagline">Electrical &amp; Computer Engineering AI</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f'<div class="v-sec-label">Appearance</div>', unsafe_allow_html=True)
    with c2:
        if st.button("☀" if DARK else "☾", key="thm", help="Toggle theme"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    st.markdown(f'<div class="v-sec-label" style="margin-top:6px">Engine</div>', unsafe_allow_html=True)
    ollama_ok = check_ollama_running()
    available_models = get_available_models() if ollama_ok else []
    if ollama_ok:
        st.markdown(f'<div class="v-status"><div class="v-dot v-dot-green"></div><span style="color:{GREEN};font-size:12px">Ollama online</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="v-status"><div class="v-dot v-dot-red"></div><span style="color:{RED};font-size:12px">Ollama offline</span></div>', unsafe_allow_html=True)
        st.code("ollama serve", language="bash")

    st.markdown(f'<div class="v-sec-label" style="margin-top:8px">Knowledge Base</div>', unsafe_allow_html=True)
    if RAG_AVAILABLE:
        kb = get_store_stats()
        if kb["status"] == "ready":
            st.markdown(f'<div class="v-status"><div class="v-dot v-dot-green"></div><span style="color:{GREEN};font-size:12px">{kb["count"]:,} chunks indexed</span></div>', unsafe_allow_html=True)
            st.markdown("<div style='margin-top:6px'>", unsafe_allow_html=True)
            for d in kb.get("domains", []):
                st.markdown(f'<span class="v-domain-tag">⚡ {d}</span>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.session_state.rag_enabled = st.toggle("Use knowledge base", value=st.session_state.rag_enabled)
        elif kb["status"] == "empty":
            st.markdown(f'<div class="v-status"><div class="v-dot v-dot-yellow"></div><span style="color:{GOLD};font-size:12px">Not built yet</span></div>', unsafe_allow_html=True)
            st.code("python rag/build_knowledge_base.py", language="bash")
        else:
            st.markdown(f'<div class="v-status"><div class="v-dot v-dot-red"></div><span style="color:{RED};font-size:12px">Not installed</span></div>', unsafe_allow_html=True)
            st.code("pip install chromadb sentence-transformers pypdf", language="bash")
    else:
        st.markdown(f'<div class="v-status"><div class="v-dot v-dot-yellow"></div><span style="color:{GOLD};font-size:12px">RAG not installed</span></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown(f'<div class="v-sec-label">Model</div>', unsafe_allow_html=True)
    if available_models:
        preferred = [m for m in RECOMMENDED_MODELS if any(m in a for a in available_models)]
        didx = 0
        if preferred:
            try:
                didx = available_models.index(next(a for a in available_models if preferred[0] in a))
            except:
                didx = 0
        st.session_state.selected_model = st.selectbox(
            "Model", available_models, index=didx, label_visibility="collapsed"
        )
    else:
        st.info("Pull a model:\n```\nollama pull deepseek-r1:7b\n```")
        st.session_state.selected_model = ""

    st.divider()

    st.markdown(f'<div class="v-sec-label">Settings</div>', unsafe_allow_html=True)
    st.session_state.temperature = st.slider(
        "Precision ↔ Creative", 0.0, 1.0,
        value=st.session_state.temperature, step=0.05
    )
    st.session_state.auto_run_code = st.toggle(
        "Auto-run Python code", value=st.session_state.auto_run_code
    )
    st.session_state.domain_filter = st.selectbox(
        "Domain filter", ["All"] + list(EXAMPLE_PROMPTS.keys())
    )

    st.divider()

    st.markdown(f'<div class="v-sec-label">Session</div>', unsafe_allow_html=True)
    n = len(st.session_state.messages)
    if n:
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;color:{MUTED};margin-bottom:8px">'
            f'{n} message{"s" if n > 1 else ""} in memory</div>',
            unsafe_allow_html=True
        )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("CLEAR", use_container_width=True):
            clear_history(st)
            st.session_state.last_citations = []
            st.rerun()
    with c2:
        st.download_button(
            "EXPORT",
            data=export_chat_markdown(st),
            file_name=f"volta_{st.session_state.session_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown(
        f'<div style="margin-top:16px;padding-top:10px;border-top:1px solid {BORDER};'
        f'font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:{MUTED};text-align:center;line-height:2;letter-spacing:1px">'
        f'VOLTA // PHASE 2 // LOCAL AI<br>FREE &amp; PRIVATE // OFFLINE</div>',
        unsafe_allow_html=True
    )


# ── HELPERS ──────────────────────────────────────────────────────
def show_exec(stdout, error, plots):
    if stdout:
        st.markdown(f'<div class="v-execout">{stdout}</div>', unsafe_allow_html=True)
    for img in plots:
        st.image(f"data:image/png;base64,{img}", use_column_width=True)
    if error:
        st.markdown(f'<div class="v-execerr">ERR // {error}</div>', unsafe_allow_html=True)


def show_cites(citations):
    if not citations:
        return
    with st.expander(f"[ {len(citations)} SOURCE{'S' if len(citations) > 1 else ''} REFERENCED ]", expanded=False):
        for c in citations:
            url = (
                f'<a href="{c["url"]}" style="color:{ACCENT};font-size:10px;'
                f'font-family:\'IBM Plex Mono\',monospace">→ {c["url"]}</a>'
            ) if c.get("url") else ""
            st.markdown(
                f'<div class="v-citebox">'
                f'<div class="v-citetit">{c["title"]}</div>'
                f'<div class="v-citedom">{c["domain"]}</div>'
                f'{url}</div>',
                unsafe_allow_html=True
            )


# ── MAIN AREA ─────────────────────────────────────────────────────
rag_badge = (
    f'<span class="v-badge v-badge-green">RAG ON</span>'
    if (RAG_AVAILABLE and st.session_state.get("rag_enabled")) else ""
)
st.markdown(f"""
<div class="v-topbar">
    <div class="v-title">
        <h1>VOLTA</h1>
        <p>Electrical &amp; Computer Engineering AI · Phase 2 · Local</p>
    </div>
    <span class="v-badge v-badge-accent">LOCAL</span>
    {rag_badge}
</div>
""", unsafe_allow_html=True)

# ── WELCOME SCREEN ──
if not st.session_state.messages:
    caps = [
        ("⚡", "Math & Sim", "Circuits, power, control, signal processing"),
        ("🏭", "PLC / SCADA", "IEC 61131-3, Ladder, ST, Modbus, OPC-UA"),
        ("💻", "Embedded", "Arduino, STM32, ESP32 · C/C++/Python"),
        ("📐", "PCB Design", "KiCad, FreeCAD, component selection"),
        ("📡", "Protocols", "CAN, RS-485, MQTT, PROFINET, EtherNet/IP"),
        ("🔋", "Power Sys", "Motors, transformers, VFDs, protection"),
    ]
    st.markdown(f'<div class="v-sec-label" style="margin-bottom:10px">Capabilities</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    for col, (icon, title, desc) in zip(cols, caps):
        with col:
            st.markdown(
                f'<div class="v-capcard">'
                f'<div class="v-capcard-icon">{icon}</div>'
                f'<div class="v-capcard-title">{title}</div>'
                f'<div class="v-capcard-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="v-sec-label" style="margin-bottom:10px">Try an example</div>', unsafe_allow_html=True)

    dom = st.session_state.domain_filter
    doms = list(EXAMPLE_PROMPTS.keys()) if dom == "All" else [dom]
    flat = [(d, p) for d in doms for p in EXAMPLE_PROMPTS.get(d, [])[:1]]

    ex_cols = st.columns(min(len(flat), 3))
    for i, (dname, prompt) in enumerate(flat[:6]):
        with ex_cols[i % 3]:
            st.markdown(
                f'<div class="v-excard">'
                f'<div class="v-exdom">{dname}</div>'
                f'<div class="v-extxt">{prompt[:110]}...</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button("→ RUN", key=f"ex_{i}", use_container_width=True):
                st.session_state._pending_prompt = prompt
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if RAG_AVAILABLE and st.session_state.get("rag_enabled"):
        kb = get_store_stats()
        if kb["status"] == "ready":
            st.success(f"📚 Knowledge base active — {kb['count']:,} chunks · {len(kb['domains'])} domains")
    else:
        st.info("💡 Run `python rag/build_knowledge_base.py` to activate citation-backed answers from real engineering references.")

    st.markdown("<br>", unsafe_allow_html=True)

# ── CHAT HISTORY ──
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<div class="v-user-wrap">'
            f'<div class="v-user-msg">{msg["content"]}</div>'
            f'<div class="v-user-av">👤</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        c1, c2 = st.columns([0.04, 0.96])
        with c1:
            st.markdown(f'<div class="v-bot-av">⚡</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(msg["content"])
            if not st.session_state.auto_run_code:
                blks = extract_code_blocks(msg["content"])
                if blks and st.button("▶ RUN CODE", key=f"run_{i}"):
                    for code in blks:
                        show_exec(*execute_code(code))

# ── PENDING EXAMPLE ──
if hasattr(st.session_state, "_pending_prompt") and st.session_state._pending_prompt:
    p = st.session_state._pending_prompt
    st.session_state._pending_prompt = None
    add_message(st, "user", p)
    st.session_state._trigger_response = True
    st.rerun()

# ── CHAT INPUT ──
user_input = st.chat_input(
    "Ask VOLTA — circuit analysis, PLC code, motor sizing, signal processing, embedded systems...",
    disabled=not st.session_state.selected_model
)
if user_input:
    add_message(st, "user", user_input)
    st.session_state._trigger_response = True
    st.rerun()

# ── GENERATE RESPONSE ──
if st.session_state.get("_trigger_response") and st.session_state.selected_model:
    st.session_state._trigger_response = False
    umsgs = [m for m in st.session_state.messages if m["role"] == "user"]
    last_q = umsgs[-1]["content"] if umsgs else ""

    cites = []
    if RAG_AVAILABLE and st.session_state.get("rag_enabled") and last_q:
        sys_p, chunks = build_rag_system_prompt(
            SYSTEM_PROMPT, last_q, st.session_state.get("domain_filter", "All")
        )
        cites = get_cited_sources(chunks)
    else:
        sys_p = SYSTEM_PROMPT

    c1, c2 = st.columns([0.04, 0.96])
    with c1:
        st.markdown(f'<div class="v-bot-av">⚡</div>', unsafe_allow_html=True)
    with c2:
        with st.chat_message("assistant", avatar="⚡"):
            ph = st.empty()
            full = ""
            with st.spinner(f"VOLTA // COMPUTING{'  [ RAG ]' if cites else ''}..."):
                for chunk in stream_chat(
                    st.session_state.selected_model,
                    get_messages_for_api(st),
                    sys_p,
                    st.session_state.temperature
                ):
                    full += chunk
                    ph.markdown(full + "▋")
            ph.markdown(full)
            add_message(st, "assistant", full)
            st.session_state.last_citations = cites
            if cites:
                show_cites(cites)
            if st.session_state.auto_run_code:
                blks = extract_code_blocks(full)
                if blks:
                    with st.expander("[ PYTHON OUTPUT ]", expanded=True):
                        for code in blks:
                            st.code(code, language="python")
                            show_exec(*execute_code(code))
