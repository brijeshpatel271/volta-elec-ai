"""
app.py — VOLTA: Electrical Engineering AI Assistant
Phase 1 MVP — Streamlit + Ollama + Python code executor

Run with:
    streamlit run app.py

Requirements:
    pip install streamlit requests matplotlib numpy scipy sympy
    + Ollama installed and running (https://ollama.com)
"""

import base64
import streamlit as st

from prompts.system_prompt import SYSTEM_PROMPT
from utils.ollama_client import (
    check_ollama_running,
    get_available_models,
    stream_chat,
    RECOMMENDED_MODELS,
)
from utils.code_executor import execute_code, extract_code_blocks
from utils.session import (
    init_session,
    add_message,
    get_messages_for_api,
    clear_history,
    export_chat_json,
    export_chat_markdown,
    EXAMPLE_PROMPTS,
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VOLTA — Engineering AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Import engineering-style font */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

/* Root variables */
:root {
    --volt-orange: #FF6B00;
    --volt-dark: #0D1117;
    --volt-surface: #161B22;
    --volt-border: #30363D;
    --volt-text: #C9D1D9;
    --volt-muted: #8B949E;
    --volt-green: #00C853;
    --volt-blue: #58A6FF;
}

/* App background */
.stApp {
    background: var(--volt-dark);
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--volt-surface);
    border-right: 1px solid var(--volt-border);
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: var(--volt-surface);
    border: 1px solid var(--volt-border);
    border-radius: 8px;
    margin-bottom: 12px;
}

/* Code blocks */
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: #0D1117 !important;
    border: 1px solid var(--volt-border) !important;
    border-radius: 6px;
}

/* Input box */
[data-testid="stChatInputContainer"] {
    background: var(--volt-surface);
    border-top: 1px solid var(--volt-border);
    padding: 12px;
}

/* VOLTA header badge */
.volta-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 0 8px;
}

.volta-badge {
    background: linear-gradient(135deg, #FF6B00, #FF9500);
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Status indicators */
.status-online { color: #00C853; font-size: 12px; }
.status-offline { color: #FF5252; font-size: 12px; }

/* Example prompt pills */
.example-pill {
    display: inline-block;
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    cursor: pointer;
    margin: 4px;
    color: #58A6FF;
}

/* Execution result box */
.exec-result {
    background: #0D1117;
    border: 1px solid #00C853;
    border-radius: 6px;
    padding: 12px;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
}

.exec-error {
    background: #0D1117;
    border: 1px solid #FF5252;
    border-radius: 6px;
    padding: 12px;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #FF5252;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INITIALIZE SESSION
# ─────────────────────────────────────────────
init_session(st)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Header
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-size: 42px;">⚡</div>
        <div style="font-size: 22px; font-weight: 600; color: #FF6B00; letter-spacing: 3px;">VOLTA</div>
        <div style="font-size: 11px; color: #8B949E; letter-spacing: 2px; text-transform: uppercase;">
            Electrical Engineering AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Ollama Status ──
    st.markdown("**🔌 Engine Status**")
    ollama_ok = check_ollama_running()
    if ollama_ok:
        st.markdown('<span class="status-online">● Ollama running</span>', unsafe_allow_html=True)
        available_models = get_available_models()
    else:
        st.markdown('<span class="status-offline">● Ollama offline</span>', unsafe_allow_html=True)
        st.warning("Start Ollama: `ollama serve`")
        available_models = []

    # ── Model Selection ──
    st.markdown("**🧠 Model**")
    if available_models:
        # Prefer recommended models if installed
        preferred = [m for m in RECOMMENDED_MODELS if any(m in a for a in available_models)]
        model_list = available_models
        default_idx = 0
        if preferred:
            try:
                default_idx = model_list.index(
                    next(a for a in available_models if preferred[0] in a)
                )
            except (StopIteration, ValueError):
                default_idx = 0

        selected = st.selectbox(
            "Select model",
            model_list,
            index=default_idx,
            label_visibility="collapsed",
        )
        st.session_state.selected_model = selected
    else:
        st.info("No models found. Pull one:")
        st.code("ollama pull deepseek-r1:7b", language="bash")
        st.session_state.selected_model = ""

    st.divider()

    # ── Settings ──
    st.markdown("**⚙️ Settings**")
    st.session_state.temperature = st.slider(
        "Creativity (temperature)",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.05,
        help="Lower = more precise/deterministic. Recommended: 0.2–0.4 for engineering",
    )

    st.session_state.auto_run_code = st.toggle(
        "Auto-run Python code",
        value=st.session_state.auto_run_code,
        help="Automatically execute Python code blocks in AI responses",
    )

    st.divider()

    # ── Domain Filter ──
    st.markdown("**📐 Domain**")
    domains = ["All"] + list(EXAMPLE_PROMPTS.keys())
    st.session_state.domain_filter = st.selectbox(
        "Filter examples by domain",
        domains,
        label_visibility="collapsed",
    )

    st.divider()

    # ── Session Controls ──
    st.markdown("**💾 Session**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear", use_container_width=True):
            clear_history(st)
            st.rerun()
    with col2:
        st.download_button(
            "📥 Export",
            data=export_chat_markdown(st),
            file_name=f"volta_{st.session_state.session_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Message count
    n_msgs = len(st.session_state.messages)
    if n_msgs:
        st.caption(f"{n_msgs} messages in session")

    st.divider()
    st.caption("VOLTA Phase 1 · Powered by Ollama")
    st.caption("Free & open-source · No data sent to cloud")


# ─────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────

# ── Top header ──
st.markdown("""
<div class="volta-header">
    <span style="font-size: 28px;">⚡</span>
    <div>
        <span style="font-size: 20px; font-weight: 600; color: #FF6B00;">VOLTA</span>
        <span style="margin-left: 10px; font-size: 13px; color: #8B949E;">
            Electrical & Computer Engineering AI · Phase 1
        </span>
    </div>
    <span class="volta-badge">LOCAL AI</span>
</div>
""", unsafe_allow_html=True)

# ── Quick-start examples (shown when chat is empty) ──
if not st.session_state.messages:
    st.markdown("### 🚀 Quick start — try an example")

    domain = st.session_state.domain_filter
    if domain == "All":
        # Show one example from each domain
        display_prompts = {k: v[:1] for k, v in EXAMPLE_PROMPTS.items()}
    else:
        display_prompts = {domain: EXAMPLE_PROMPTS.get(domain, [])}

    cols = st.columns(len(display_prompts) if len(display_prompts) <= 3 else 3)
    flat_prompts = [(domain, prompt) for domain, prompts in display_prompts.items() for prompt in prompts]

    for i, (domain_name, prompt) in enumerate(flat_prompts[:6]):
        col = cols[i % len(cols)]
        with col:
            with st.container(border=True):
                st.markdown(f"**{domain_name}**")
                st.markdown(f"<small>{prompt[:100]}...</small>", unsafe_allow_html=True)
                if st.button("Try this →", key=f"example_{i}", use_container_width=True):
                    st.session_state._pending_prompt = prompt
                    st.rerun()

    st.divider()

    # Capabilities overview
    st.markdown("### 🔧 What VOLTA can do")
    cap_cols = st.columns(4)
    capabilities = [
        ("🔢", "Math & Simulation", "Circuit analysis, power systems, control theory, signal processing with Python code"),
        ("🏭", "PLC / SCADA", "IEC 61131-3 code, ladder logic, Modbus, OPC-UA, HMI design"),
        ("💻", "Embedded Code", "Arduino, STM32, ESP32, Raspberry Pi — C/C++/Python/MicroPython"),
        ("📐", "Design Guidance", "Component selection, PCB tips, 3D enclosures, KiCad, FreeCAD"),
    ]
    for col, (icon, title, desc) in zip(cap_cols, capabilities):
        with col:
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)

    st.divider()


# ── Display chat history ──
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚡"):
        st.markdown(msg["content"])

        # If this is an assistant message with code, show a run button
        if msg["role"] == "assistant" and not st.session_state.auto_run_code:
            code_blocks = extract_code_blocks(msg["content"])
            if code_blocks:
                if st.button(f"▶ Run Python code", key=f"run_{i}"):
                    for code in code_blocks:
                        stdout, error, plots = execute_code(code)
                        _display_execution_result(stdout, error, plots)


def _display_execution_result(stdout: str, error: str, plots: list) -> None:
    """Helper: render code execution output in the UI."""
    if stdout:
        st.markdown('<div class="exec-result">', unsafe_allow_html=True)
        st.text(stdout)
        st.markdown('</div>', unsafe_allow_html=True)
    if plots:
        for img_b64 in plots:
            st.image(
                f"data:image/png;base64,{img_b64}",
                use_column_width=True,
            )
    if error:
        st.markdown('<div class="exec-error">', unsafe_allow_html=True)
        st.text(f"⚠ Error:\n{error}")
        st.markdown('</div>', unsafe_allow_html=True)


# ── Handle example prompt clicks ──
if hasattr(st.session_state, "_pending_prompt") and st.session_state._pending_prompt:
    pending = st.session_state._pending_prompt
    st.session_state._pending_prompt = None
    # Feed it as if the user typed it
    add_message(st, "user", pending)
    with st.chat_message("user", avatar="👤"):
        st.markdown(pending)
    st.session_state._trigger_response = True
    st.rerun()


# ── Chat input ──
user_input = st.chat_input(
    "Ask anything — circuit analysis, PLC code, motor sizing, 3D design, signal processing...",
    disabled=not st.session_state.selected_model,
)

if user_input:
    add_message(st, "user", user_input)
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state._trigger_response = True


# ── Generate AI response ──
if st.session_state.get("_trigger_response") and st.session_state.selected_model:
    st.session_state._trigger_response = False

    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full_response = ""

        with st.spinner("VOLTA is thinking..."):
            for chunk in stream_chat(
                model=st.session_state.selected_model,
                messages=get_messages_for_api(st),
                system_prompt=SYSTEM_PROMPT,
                temperature=st.session_state.temperature,
            ):
                full_response += chunk
                # Stream tokens to screen
                placeholder.markdown(full_response + "▋")

        placeholder.markdown(full_response)
        add_message(st, "assistant", full_response)

        # ── Auto-run Python code if enabled ──
        if st.session_state.auto_run_code:
            code_blocks = extract_code_blocks(full_response)
            if code_blocks:
                with st.expander("🐍 Python execution output", expanded=True):
                    for code in code_blocks:
                        st.code(code, language="python")
                        stdout, error, plots = execute_code(code)
                        _display_execution_result(stdout, error, plots)

elif not st.session_state.selected_model and user_input:
    st.warning("⚡ Please select a model in the sidebar first. Make sure Ollama is running.")
