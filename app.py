import sys
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import streamlit as st
from src.orchestrator.orchestrator import GitaGPTOrchestrator

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gita GPT",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0b0d14 !important;
    color: #e8dfc8 !important;
}
[data-testid="stSidebar"] {
    background: #0f1120 !important;
    border-right: 1px solid #2a2040;
}
[data-testid="stSidebar"] * { color: #c9bfa8 !important; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-bottom: 1px solid #2a2040;
    margin-bottom: 1.5rem;
}
.hero-om {
    font-size: 3rem;
    color: #d4a017;
    line-height: 1;
}
.hero-title {
    font-family: 'Cinzel', serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #d4a017, #f5e49c, #d4a017);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.06em;
    margin: 0.2rem 0;
}
.hero-sub {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: #9a8f7a;
    letter-spacing: 0.03em;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: #131626 !important;
    border: 1px solid #3a2f5a !important;
    border-radius: 12px !important;
    color: #e8dfc8 !important;
    font-family: 'Lora', serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
    caret-color: #d4a017;
}
.stTextInput > div > div > input:focus {
    border-color: #d4a017 !important;
    box-shadow: 0 0 0 2px rgba(212, 160, 23, 0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #5a5070 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6b3fa0, #3d1f6e) !important;
    color: #f5e49c !important;
    border: 1px solid #9b6dcc !important;
    border-radius: 10px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #7d50b8, #4e2882) !important;
    border-color: #d4a017 !important;
    box-shadow: 0 0 12px rgba(212, 160, 23, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* ── Verse card ── */
.verse-card {
    background: linear-gradient(145deg, #131626, #1a1830);
    border: 1px solid #2e2448;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
}
.verse-card::before {
    content: "ॐ";
    position: absolute;
    top: -10px;
    right: 20px;
    font-size: 6rem;
    color: rgba(212,160,23,0.04);
    font-family: serif;
    pointer-events: none;
}
.verse-ref {
    font-family: 'Cinzel', serif;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #d4a017;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.verse-chapter-theme {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.78rem;
    color: #7a6e8a;
    margin-bottom: 1rem;
}
.verse-sanskrit {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 1.05rem;
    color: #c4a35a;
    line-height: 1.8;
    border-left: 3px solid #d4a017;
    padding-left: 1rem;
    margin-bottom: 1rem;
}
.verse-translation {
    font-family: 'Lora', serif;
    font-size: 1rem;
    color: #d8d0bc;
    line-height: 1.75;
    margin-bottom: 0.5rem;
}

/* ── Interpretation card ── */
.interp-card {
    background: linear-gradient(145deg, #0f1a1f, #131f25);
    border: 1px solid #1e3a3a;
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
}
.section-label {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    color: #5a9e8a;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}
.interp-text {
    font-family: 'Lora', serif;
    font-size: 1rem;
    color: #ccd8d2;
    line-height: 1.85;
}

/* ── Tag pills ── */
.tag-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.tag {
    display: inline-block;
    padding: 0.22rem 0.7rem;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.03em;
}
.tag-theme { background: #1e1535; color: #9b78cc; border: 1px solid #3a2860; }
.tag-practice { background: #0e2020; color: #5a9e7a; border: 1px solid #1a4040; }
.tag-verse { background: #1a1a0e; color: #b8a040; border: 1px solid #3a3018; }

/* ── Supporting verses ── */
.support-card {
    background: #0f1120;
    border: 1px solid #1e1a30;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
}
.support-ref { font-family: 'Cinzel', serif; font-size: 0.72rem; color: #7a6090; letter-spacing: 0.1em; }
.support-text { font-family: 'Lora', serif; font-size: 0.88rem; color: #a09888; line-height: 1.6; margin-top: 0.25rem; }

/* ── Contradiction badge ── */
.contradiction-badge {
    background: #1a0e0a;
    border: 1px solid #4a2a1a;
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: #c07040;
    margin-bottom: 0.4rem;
}

/* ── Refusal card ── */
.refusal-card {
    background: #100e1a;
    border: 1px solid #2a1e3a;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}
.refusal-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.refusal-title {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    color: #9b78cc;
    margin-bottom: 0.8rem;
}
.refusal-text { font-family: 'Lora', serif; font-size: 0.95rem; color: #8a7a98; line-height: 1.7; }

/* ── Chat history item ── */
.history-item {
    padding: 0.5rem 0.6rem;
    margin-bottom: 0.3rem;
    border-radius: 8px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s;
}
.history-item:hover { background: #1a1530; border-color: #2e2448; }
.history-q { font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #c4b8d8; }
.history-v { font-family: 'Cinzel', serif; font-size: 0.68rem; color: #7a6090; letter-spacing: 0.08em; margin-top: 0.15rem; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #d4a017 !important; }
[data-testid="stStatusWidget"] { color: #d4a017 !important; }

/* ── Divider ── */
hr { border-color: #2a2040 !important; }

/* ── Confidence bar ── */
.conf-bar-wrap { margin-top: 0.4rem; }
.conf-label { font-family: 'Inter', sans-serif; font-size: 0.72rem; color: #6a6080; }
.conf-bar { height: 3px; background: #1e1830; border-radius: 2px; margin-top: 0.2rem; }
.conf-fill { height: 3px; border-radius: 2px; background: linear-gradient(90deg, #3a6090, #d4a017); }
</style>
""", unsafe_allow_html=True)


# ── Orchestrator (cached) ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading sacred wisdom...")
def get_orchestrator():
    return GitaGPTOrchestrator()


# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []   # list of dicts
if "current" not in st.session_state:
    st.session_state.current = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ॐ  Gita GPT")
    st.markdown("<p style='font-size:0.78rem;color:#6a5a80;font-family:Lora,serif;font-style:italic;'>Seek wisdom grounded in the Bhagavad Gita</p>", unsafe_allow_html=True)
    st.divider()

    if st.button("✦  New Conversation", use_container_width=True):
        orc = get_orchestrator()
        orc.reset_memory()
        st.session_state.history = []
        st.session_state.current = None
        st.rerun()

    if st.session_state.history:
        st.markdown("<p style='font-family:Cinzel,serif;font-size:0.7rem;letter-spacing:0.12em;color:#5a4a70;text-transform:uppercase;margin-top:1rem;'>Recent Questions</p>", unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            verse_label = item.get("verse_ref", "") if not item.get("is_refusal") else "—"
            st.markdown(f"""
            <div class="history-item">
                <div class="history-q">{item['query'][:52]}{'…' if len(item['query'])>52 else ''}</div>
                <div class="history-v">{verse_label}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='font-size:0.72rem;color:#4a3a58;font-family:Inter,sans-serif;text-align:center;'>No verse is invented.<br>LLMs interpret, not generate.</p>", unsafe_allow_html=True)


# ── Main layout ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-om">ॐ</div>
    <div class="hero-title">Gita GPT</div>
    <div class="hero-sub">Grounded wisdom from the Bhagavad Gita · Agentic RAG</div>
</div>
""", unsafe_allow_html=True)

# Example queries
EXAMPLES = [
    "How do I deal with anger?",
    "What is the nature of the self?",
    "Should I focus on results or just do my work?",
    "How can I find peace amid suffering?",
    "What does the Gita say about duty?",
]

col_ex, *_ = st.columns([5, 1])
with col_ex:
    st.markdown("<p style='font-family:Inter,sans-serif;font-size:0.8rem;color:#5a4a70;margin-bottom:0.4rem;'>Try asking:</p>", unsafe_allow_html=True)
    ex_cols = st.columns(len(EXAMPLES))
    for col, ex in zip(ex_cols, EXAMPLES):
        with col:
            if st.button(ex, key=f"ex_{ex[:10]}", use_container_width=True):
                st.session_state.pending_query = ex

# Query input
with st.form("query_form", clear_on_submit=True):
    cols = st.columns([6, 1])
    with cols[0]:
        query = st.text_input(
            "Ask the Gita",
            placeholder="What weighs on your mind? Ask with sincerity…",
            label_visibility="collapsed",
            key="query_field",
        )
    with cols[1]:
        submitted = st.form_submit_button("Ask  ›", use_container_width=True)

# Example button click acts as an immediate submission
if "pending_query" in st.session_state and st.session_state.pending_query:
    pending = st.session_state.pending_query
    st.session_state.pending_query = ""
    orc = get_orchestrator()
    with st.spinner("Seeking wisdom from the Gita…"):
        result = orc.process_query_structured(pending)
    st.session_state.history.append(result)
    st.session_state.current = result
    st.rerun()

if submitted and query and query.strip():
    st.session_state.query_input = ""
    orc = get_orchestrator()
    with st.spinner("Seeking wisdom from the Gita…"):
        result = orc.process_query_structured(query.strip())
    st.session_state.history.append(result)
    st.session_state.current = result
    st.rerun()

# ── Response display ───────────────────────────────────────────────────────────
current = st.session_state.current

if current is None:
    if not st.session_state.history:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
            <div style='font-size:3.5rem;margin-bottom:1rem;opacity:0.25;'>🪷</div>
            <p style='font-family:Lora,serif;font-style:italic;font-size:1.05rem;color:#4a4060;'>
                "You have a right to perform your prescribed duties,<br>
                but you are not entitled to the fruits of your actions."
            </p>
            <p style='font-family:Cinzel,serif;font-size:0.72rem;color:#3a3050;letter-spacing:0.12em;margin-top:0.5rem;'>
                — BHAGAVAD GITA 2.47
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    if current.get("is_refusal"):
        st.markdown(f"""
        <div class="refusal-card">
            <div class="refusal-icon">🙏</div>
            <div class="refusal-title">Beyond the Gita's Scope</div>
            <div class="refusal-text">{current.get('refusal_message','This question falls outside what the Bhagavad Gita directly addresses.')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        left, right = st.columns([3, 2], gap="large")

        with left:
            # Verse card
            themes_html = "".join(f'<span class="tag tag-theme">{t}</span>' for t in current.get("themes", [])[:4])
            chapter_theme_html = f'<div class="verse-chapter-theme">{current["chapter_theme"]}</div>' if current.get("chapter_theme") else ""
            st.markdown(f"""
            <div class="verse-card">
                <div class="verse-ref">{current['verse_ref']}</div>
                {chapter_theme_html}
                <div class="verse-sanskrit">{current['sanskrit']}</div>
                <div class="verse-translation">{current['translation']}</div>
                <div class="tag-row">{themes_html}</div>
            </div>
            """, unsafe_allow_html=True)

            # Interpretation
            interp = current.get("interpretation", "").strip()
            if interp:
                st.markdown(f"""
                <div class="interp-card">
                    <div class="section-label">Interpretation · Applied to Your Question</div>
                    <div class="interp-text">{interp}</div>
                </div>
                """, unsafe_allow_html=True)

            # Supportive practices
            practices = current.get("supportive_practices", [])
            if practices:
                tags_html = "".join(f'<span class="tag tag-practice">{p}</span>' for p in practices)
                st.markdown(f"""
                <div style="margin-bottom:1.2rem;">
                    <div class="section-label" style="margin-bottom:0.5rem;">Supportive Practices</div>
                    <div class="tag-row">{tags_html}</div>
                </div>
                """, unsafe_allow_html=True)

        with right:
            # Your query
            st.markdown(f"""
            <div style="margin-bottom:1rem;padding:0.9rem 1.1rem;background:#0f0e18;border:1px solid #1e1830;border-radius:10px;">
                <div class="section-label">Your Question</div>
                <p style="font-family:Lora,serif;font-style:italic;font-size:0.95rem;color:#b8b0c8;margin:0;">"{current['query']}"</p>
            </div>
            """, unsafe_allow_html=True)

            # Confidence
            conf = current.get("retrieval_confidence", 0)
            conf_pct = int(min(conf * 100, 100))
            st.markdown(f"""
            <div class="conf-bar-wrap">
                <div class="conf-label">Retrieval confidence · {conf_pct}%</div>
                <div class="conf-bar"><div class="conf-fill" style="width:{conf_pct}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)

            # Contradictions
            contradictions = current.get("contradictions", [])
            if contradictions:
                st.markdown("<div style='margin-top:1rem;'><div class='section-label'>Thematic Tensions Detected</div>", unsafe_allow_html=True)
                for c in contradictions:
                    st.markdown(f'<div class="contradiction-badge">⟐ {c}</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Core teaching note
            core = current.get("core_teaching", "")
            if core and core != current.get("translation", ""):
                st.markdown(f"""
                <div style='margin-top:1rem;padding:0.9rem 1.1rem;background:#0a100a;border:1px solid #1a2a1a;border-radius:10px;'>
                    <div class='section-label'>Core Teaching</div>
                    <p style='font-family:Lora,serif;font-size:0.88rem;color:#88a888;line-height:1.65;margin:0;'>{core}</p>
                </div>
                """, unsafe_allow_html=True)

# ── History strip at bottom ────────────────────────────────────────────────────
if len(st.session_state.history) > 1:
    st.divider()
    st.markdown("<p style='font-family:Cinzel,serif;font-size:0.72rem;letter-spacing:0.12em;color:#4a3a58;text-transform:uppercase;'>Previous Questions This Session</p>", unsafe_allow_html=True)
    cols = st.columns(min(len(st.session_state.history) - 1, 4))
    for i, item in enumerate(reversed(st.session_state.history[:-1][:4])):
        with cols[i]:
            label = item["query"][:38] + ("…" if len(item["query"]) > 38 else "")
            verse = item.get("verse_ref", "—") if not item.get("is_refusal") else "—"
            if st.button(f"{label}\n{verse}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current = item
                st.rerun()
