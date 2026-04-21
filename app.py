import sys
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import streamlit as st
from src.orchestrator.orchestrator import GitaGPTOrchestrator

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic RAG for Grounded Ethical Reasoning",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0b0d14 !important;
    color: #e8dfc8 !important;
}
[data-testid="stSidebar"] {
    background: #0f1120 !important;
    border-right: 1px solid #1e1a30;
}
[data-testid="stSidebar"] * { color: #c9bfa8 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1200px !important;
}

/* Hero */
.hero {
    text-align: center;
    padding: 1.6rem 1rem 1.2rem;
    border-bottom: 1px solid #1e1a30;
    margin-bottom: 1.4rem;
}
.hero-om { font-size: 2.8rem; color: #d4a017; line-height: 1; }
.hero-title {
    font-family: 'Cinzel', serif;
    font-size: 1.35rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c49010, #f5e49c, #c49010);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.04em;
    line-height: 1.55;
    margin: 0.3rem 0 0.35rem;
}
.hero-sub {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.88rem;
    color: #7a7060;
}

/* Input */
.stTextInput > div > div > input {
    background: #10121e !important;
    border: 1px solid #2e2448 !important;
    border-radius: 10px !important;
    color: #e8dfc8 !important;
    font-family: 'Lora', serif !important;
    font-size: 0.97rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #d4a017 !important;
    box-shadow: 0 0 0 2px rgba(212,160,23,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: #3e3858 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #5a2d8a, #331660) !important;
    color: #f0e08a !important;
    border: 1px solid #7a50b0 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 0.45rem 0.9rem !important;
    transition: all 0.18s !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6e3aa8, #422080) !important;
    border-color: #d4a017 !important;
    box-shadow: 0 0 10px rgba(212,160,23,0.2) !important;
    transform: translateY(-1px) !important;
}
/* Cards */
.verse-card {
    background: linear-gradient(160deg, #131626, #191730);
    border: 1px solid #2a2048;
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.verse-card::before {
    content: "ॐ";
    position: absolute; top: -8px; right: 16px;
    font-size: 5rem;
    color: rgba(212,160,23,0.05);
    pointer-events: none;
}
.verse-ref {
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    color: #d4a017;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}
.chapter-theme {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.76rem;
    color: #6a5e7a;
    margin-bottom: 0.9rem;
}
.sanskrit {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 1rem;
    color: #c4a35a;
    line-height: 1.75;
    border-left: 3px solid #d4a017;
    padding-left: 0.9rem;
    margin-bottom: 0.9rem;
}
.translation {
    font-family: 'Lora', serif;
    font-size: 0.95rem;
    color: #d0c8b8;
    line-height: 1.72;
}
.tag-row { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.7rem; }
.tag {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 500;
}
.tag-theme { background: #1a1230; color: #9070c0; border: 1px solid #302050; }
.tag-practice { background: #0c1c1c; color: #508870; border: 1px solid #183030; }

.interp-card {
    background: linear-gradient(160deg, #0e1820, #121c24);
    border: 1px solid #1a3030;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    min-height: 80px;
}
.section-label {
    font-family: 'Cinzel', serif;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: #407a68;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.interp-text {
    font-family: 'Lora', serif;
    font-size: 0.95rem;
    color: #c0ccc8;
    line-height: 1.82;
    white-space: pre-wrap;
}

.info-card {
    background: #0e0e1a;
    border: 1px solid #1a1828;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.8rem;
}
.info-label {
    font-family: 'Cinzel', serif;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    color: #504870;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}
.info-text {
    font-family: 'Lora', serif;
    font-size: 0.88rem;
    color: #a098b8;
    line-height: 1.6;
    font-style: italic;
}

.contradiction-badge {
    background: #180e0a;
    border: 1px solid #3a2010;
    border-radius: 7px;
    padding: 0.4rem 0.75rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.74rem;
    color: #b06030;
    margin-bottom: 0.35rem;
}

.refusal-card {
    background: #0e0c1a;
    border: 1px solid #201830;
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-top: 1rem;
}
.refusal-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.refusal-title { font-family: 'Cinzel', serif; font-size: 1rem; color: #8060a8; margin-bottom: 0.6rem; }
.refusal-text { font-family: 'Lora', serif; font-size: 0.92rem; color: #706080; line-height: 1.7; }

.history-q { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #b8aec8; }
.history-v { font-family: 'Cinzel', serif; font-size: 0.66rem; color: #604e78; letter-spacing: 0.08em; }
hr { border-color: #1e1830 !important; }
.stSpinner > div { border-top-color: #d4a017 !important; }
</style>
""", unsafe_allow_html=True)


# ── Orchestrator ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading sacred wisdom…")
def get_orchestrator():
    return GitaGPTOrchestrator()


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [("history", []), ("current", None), ("pending_query", "")]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<p style='font-family:Cinzel,serif;font-size:0.82rem;font-weight:600;color:#d4a017;letter-spacing:0.04em;line-height:1.5;margin-bottom:0.2rem;'>Agentic RAG System<br>for Grounded Ethical Reasoning</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.72rem;color:#504868;font-family:Lora,serif;font-style:italic;'>Bhagavad Gita · Agentic RAG</p>", unsafe_allow_html=True)
    st.divider()
    if st.button("✦  New Conversation", use_container_width=True):
        get_orchestrator().reset_memory()
        st.session_state.history = []
        st.session_state.current = None
        st.rerun()
    if st.session_state.history:
        st.markdown("<p style='font-family:Cinzel,serif;font-size:0.66rem;letter-spacing:0.12em;color:#403858;text-transform:uppercase;margin-top:1rem;'>Recent</p>", unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-6:]):
            verse = item.get("verse_ref", "—") if not item.get("is_refusal") else "—"
            q = item["query"]
            st.markdown(f"""
            <div style='padding:0.45rem 0.5rem;margin-bottom:0.25rem;border-radius:7px;border:1px solid #181428;'>
                <div class='history-q'>{q[:50]}{'…' if len(q)>50 else ''}</div>
                <div class='history-v'>{verse}</div>
            </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='font-size:0.7rem;color:#382e48;font-family:Inter,sans-serif;text-align:center;'>No verse is invented.<br>LLMs interpret, never fabricate.</p>", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-om">ॐ</div>
    <div class="hero-title">Design and Implementation of an Agentic<br>Retrieval-Augmented Generation (RAG) System<br>for Grounded Ethical Reasoning</div>
    <div class="hero-sub">Grounded in the Bhagavad Gita · Agentic RAG Pipeline</div>
</div>
""", unsafe_allow_html=True)


# ── Example buttons ───────────────────────────────────────────────────────────
EXAMPLES = [
    "How to overcome anger & fear?",
    "What is the eternal self (Atman)?",
    "How to act without attachment?",
    "Path to inner peace & equanimity",
    "What is one's true dharma?",
]

st.markdown("<p style='font-family:Inter,sans-serif;font-size:0.76rem;color:#403858;margin-bottom:0.4rem;'>Try asking</p>", unsafe_allow_html=True)
ex_cols = st.columns(5)
for i, (col, ex) in enumerate(zip(ex_cols, EXAMPLES)):
    with col:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state.pending_query = ex


# ── Query input (no form — only Ask button triggers submission) ───────────────
c1, c2 = st.columns([8, 1])
with c1:
    typed_query = st.text_input(
        "query",
        placeholder="What weighs on your mind? Ask with sincerity…",
        label_visibility="collapsed",
        key="query_field",
    )
with c2:
    ask_clicked = st.button("Ask ›", use_container_width=True)


# ── Determine which query to run ──────────────────────────────────────────────
query_to_run = ""
if ask_clicked and typed_query and typed_query.strip():
    query_to_run = typed_query.strip()
elif st.session_state.pending_query:
    query_to_run = st.session_state.pending_query
    st.session_state.pending_query = ""


# ── Process & render ──────────────────────────────────────────────────────────
def render_right_panel(result):
    contradictions = result.get("contradictions", [])
    core = result.get("core_teaching", "")
    translation = result.get("translation", "")

    html = f"""
    <div class="info-card" style="margin-bottom:0.8rem;">
        <div class="info-label">Your Question</div>
        <div class="info-text">"{result['query']}"</div>
    </div>"""

    if contradictions:
        html += "<div style='margin-top:0.8rem;'><div class='section-label'>Thematic Tensions</div>"
        for c in contradictions:
            html += f'<div class="contradiction-badge">⟐ {c}</div>'
        html += "</div>"

    if core and core != translation:
        html += f"""
        <div class="info-card" style="margin-top:0.8rem;background:#0a100a;border-color:#182018;">
            <div class="info-label">Core Teaching</div>
            <div class="info-text" style="color:#7a9878;">{core}</div>
        </div>"""

    return html


if query_to_run:
    orc = get_orchestrator()
    left, right = st.columns([3, 2], gap="large")

    with st.spinner("Finding relevant verse…"):
        result, state = orc.process_query_fast(query_to_run)

    if result.get("is_refusal"):
        st.markdown(f"""
        <div class="refusal-card">
            <div class="refusal-icon">🙏</div>
            <div class="refusal-title">Beyond the Gita's Scope</div>
            <div class="refusal-text">{result.get('refusal_message','This question falls outside what the Bhagavad Gita directly addresses.')}</div>
        </div>""", unsafe_allow_html=True)
        st.session_state.history.append(result)
        st.session_state.current = result
    else:
        # Show verse card instantly
        themes_html = "".join(f'<span class="tag tag-theme">{t}</span>' for t in result.get("themes", [])[:4])
        ct = result.get("chapter_theme", "")
        ct_html = f'<div class="chapter-theme">{ct}</div>' if ct else ""

        with left:
            st.markdown(f"""
            <div class="verse-card">
                <div class="verse-ref">{result['verse_ref']}</div>
                {ct_html}
                <div class="sanskrit">{result['sanskrit']}</div>
                <div class="translation">{result['translation']}</div>
                <div class="tag-row">{themes_html}</div>
            </div>""", unsafe_allow_html=True)

            # Stream interpretation
            st.markdown('<div class="interp-card"><div class="section-label">Interpretation · Applied to Your Question</div>', unsafe_allow_html=True)
            interp_slot = st.empty()
            full_interp = ""
            for chunk in orc.stream_interpretation(state):
                full_interp += chunk
                interp_slot.markdown(f'<div class="interp-text">{full_interp}▌</div>', unsafe_allow_html=True)
            interp_slot.markdown(f'<div class="interp-text">{full_interp}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            practices = result.get("supportive_practices", [])
            if practices:
                tags_html = "".join(f'<span class="tag tag-practice">{p}</span>' for p in practices)
                st.markdown(f"""
                <div style="margin-top:0.2rem;">
                    <div class="section-label">Supportive Practices</div>
                    <div class="tag-row">{tags_html}</div>
                </div>""", unsafe_allow_html=True)

        with right:
            st.markdown(render_right_panel(result), unsafe_allow_html=True)

        result["interpretation"] = full_interp
        st.session_state.history.append(result)
        st.session_state.current = result

elif st.session_state.current is not None:
    current = st.session_state.current

    if current.get("is_refusal"):
        st.markdown(f"""
        <div class="refusal-card">
            <div class="refusal-icon">🙏</div>
            <div class="refusal-title">Beyond the Gita's Scope</div>
            <div class="refusal-text">{current.get('refusal_message','')}</div>
        </div>""", unsafe_allow_html=True)
    else:
        left, right = st.columns([3, 2], gap="large")
        themes_html = "".join(f'<span class="tag tag-theme">{t}</span>' for t in current.get("themes", [])[:4])
        ct = current.get("chapter_theme", "")
        ct_html = f'<div class="chapter-theme">{ct}</div>' if ct else ""
        interp = current.get("interpretation", "").strip()

        with left:
            st.markdown(f"""
            <div class="verse-card">
                <div class="verse-ref">{current['verse_ref']}</div>
                {ct_html}
                <div class="sanskrit">{current['sanskrit']}</div>
                <div class="translation">{current['translation']}</div>
                <div class="tag-row">{themes_html}</div>
            </div>""", unsafe_allow_html=True)

            if interp:
                st.markdown(f"""
                <div class="interp-card">
                    <div class="section-label">Interpretation · Applied to Your Question</div>
                    <div class="interp-text">{interp}</div>
                </div>""", unsafe_allow_html=True)

            practices = current.get("supportive_practices", [])
            if practices:
                tags_html = "".join(f'<span class="tag tag-practice">{p}</span>' for p in practices)
                st.markdown(f"""
                <div style="margin-top:0.2rem;">
                    <div class="section-label">Supportive Practices</div>
                    <div class="tag-row">{tags_html}</div>
                </div>""", unsafe_allow_html=True)

        with right:
            st.markdown(render_right_panel(current), unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:3.5rem 2rem;'>
        <div style='font-size:3rem;opacity:0.15;margin-bottom:1rem;'>🪷</div>
        <p style='font-family:Lora,serif;font-style:italic;font-size:1rem;color:#3a3458;'>
            "You have a right to perform your prescribed duties,<br>
            but you are not entitled to the fruits of your actions."
        </p>
        <p style='font-family:Cinzel,serif;font-size:0.68rem;color:#2e2848;letter-spacing:0.12em;margin-top:0.5rem;'>
            — BHAGAVAD GITA 2.47
        </p>
    </div>""", unsafe_allow_html=True)


# ── History strip ─────────────────────────────────────────────────────────────
if len(st.session_state.history) > 1:
    st.divider()
    st.markdown("<p style='font-family:Cinzel,serif;font-size:0.66rem;letter-spacing:0.12em;color:#382e48;text-transform:uppercase;'>Previous Questions</p>", unsafe_allow_html=True)
    prev_items = [i for i in st.session_state.history[:-1]][-4:]
    hist_cols = st.columns(min(len(prev_items), 4))
    for i, item in enumerate(reversed(prev_items)):
        with hist_cols[i]:
            label = item["query"][:36] + ("…" if len(item["query"]) > 36 else "")
            verse = item.get("verse_ref", "—") if not item.get("is_refusal") else "—"
            if st.button(f"{label}\n{verse}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current = item
                st.rerun()
