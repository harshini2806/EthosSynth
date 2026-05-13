"""
streamlit_app.py — The frontend UI (redesigned)

Run locally with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import os

# --- Config ---
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Page Setup ---
st.set_page_config(
    page_title="Moral Dilemma Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400;1,500&display=swap');

    /* ─── Reset & Base ─────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'EB Garamond', serif;
        background-color: #080608 !important;
        color: #ede8e0;
    }

    .stApp { background-color: #080608; }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 60px 60px 80px !important;
        max-width: 1200px !important;
    }

    /* ─── Animated Background Orbs ─────────────────── */
    .bg-canvas {
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
    }
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.10;
        animation: drift 20s ease-in-out infinite alternate;
    }
    .orb1 { width: 700px; height: 700px; background: #8B6914; top: -250px; left: -150px; animation-delay: 0s; }
    .orb2 { width: 500px; height: 500px; background: #6B3D8A; top: 35%; right: -120px; animation-delay: -7s; }
    .orb3 { width: 380px; height: 380px; background: #1A5C4A; bottom: -80px; left: 28%; animation-delay: -13s; }
    .orb4 { width: 250px; height: 250px; background: #8B2020; top: 70%; left: 10%; animation-delay: -4s; }

    @keyframes drift {
        from { transform: translate(0, 0) scale(1); }
        to   { transform: translate(40px, -25px) scale(1.1); }
    }

    /* ─── Header ────────────────────────────────────── */
    .page-header {
        text-align: center;
        margin-bottom: 64px;
        position: relative;
    }

    .eyebrow {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        font-size: 13px;
        letter-spacing: 5px;
        color: #c9a84c;
        text-transform: uppercase;
        margin-bottom: 20px;
        opacity: 0.65;
    }

    .main-title {
        font-family: 'Cinzel', serif;
        font-size: clamp(2.6rem, 5.5vw, 4.8rem);
        font-weight: 700;
        line-height: 1.05;
        background: linear-gradient(135deg, #f0dfa8 0%, #c9a84c 45%, #957218 75%, #c9a84c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }

    .ornament-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin: 20px 0 22px;
    }
    .ornament-line {
        width: 90px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #c9a84c55, transparent);
    }
    .ornament-icon { color: #c9a84c; font-size: 20px; opacity: 0.55; }

    .subtitle {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        font-size: 1.2rem;
        color: #8a7860;
        letter-spacing: 0.2px;
    }

    /* ─── Input Panels ──────────────────────────────── */
    .panel {
        background: rgba(255, 255, 255, 0.022);
        border: 1px solid rgba(201, 168, 76, 0.13);
        border-radius: 18px;
        padding: 28px 30px;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
        transition: border-color 0.3s;
    }
    .panel::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(201,168,76,0.035) 0%, transparent 55%);
        border-radius: 18px;
        pointer-events: none;
    }
    .panel:hover { border-color: rgba(201,168,76,0.22); }

    .panel-label {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        font-size: 11px;
        letter-spacing: 3.5px;
        text-transform: uppercase;
        color: #c9a84c;
        margin-bottom: 14px;
        opacity: 0.65;
    }

    /* ─── Streamlit widget overrides ───────────────── */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(201, 168, 76, 0.18) !important;
        border-radius: 12px !important;
        color: #c8bfa8 !important;
        font-family: 'EB Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
        caret-color: #c9a84c !important;
        transition: border-color 0.3s !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(201, 168, 76, 0.45) !important;
        box-shadow: 0 0 0 3px rgba(201, 168, 76, 0.07) !important;
    }
    .stTextArea textarea::placeholder { color: #4a4030 !important; }

    .stMultiSelect [data-baseweb="select"] > div:first-child {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(201, 168, 76, 0.2) !important;
        border-radius: 10px !important;
        color: #c8bfa8 !important;
        font-family: 'EB Garamond', serif !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background: rgba(201, 168, 76, 0.12) !important;
        border: 1px solid rgba(201, 168, 76, 0.3) !important;
        color: #c9a84c !important;
        border-radius: 20px !important;
        font-family: 'EB Garamond', serif !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: #9a8870;
        font-family: 'EB Garamond', serif;
        font-size: 0.95rem;
    }

    /* ─── Analyze Button ────────────────────────────── */
    /* ─── Analyze Button ────────────────────────────── */
    .stButton > button {
        width: 100%;
        padding: 18px 40px !important;
        background: linear-gradient(135deg, #7a5c0e 0%, #c9a84c 45%, #7a5c0e 100%) !important;
        background-size: 200% 100% !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Cinzel', serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 3.5px !important;
        color: rgb(0, 0, 0) !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
        transition: all 0.35s ease !important;
        margin-bottom: 0 !important;
        position: relative;
        overflow: hidden;
    }

    /* Add this right here to override the global p tag color */
    .stButton > button p {
        color:rgb(88, 65, 1) !important;
        font-weight: 800 !important;
        margin: 0 !important; /* Ensures it doesn't mess up your vertical alignment */
    }

    .stButton > button:hover {
        box-shadow: 0 6px 35px rgba(201, 168, 76, 0.28) !important;
        background-position: 100% 0 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ─── Section Divider ───────────────────────────── */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 20px;
        margin: 52px 0 32px;
    }
    .section-divider-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(201,168,76,0.25), transparent);
    }
    .section-divider-label {
        font-family: 'Cinzel', serif;
        font-size: 10px;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #c9a84c;
        opacity: 0.5;
        white-space: nowrap;
    }

    /* ─── Philosophy Cards ──────────────────────────── */
    .philosophy-card {
        background: rgba(255, 255, 255, 0.022);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 26px 26px 22px;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        height: 100%;
    }
    .philosophy-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(201,168,76,0.35), transparent);
    }
    .philosophy-card:hover {
        transform: translateY(-4px);
        border-color: rgba(201,168,76,0.18);
        box-shadow: 0 16px 48px rgba(0,0,0,0.35);
    }

    .card-index {
        position: absolute;
        top: 18px; right: 20px;
        font-family: 'Cinzel', serif;
        font-size: 48px;
        font-weight: 700;
        color: rgba(201,168,76,0.055);
        line-height: 1;
        user-select: none;
    }

    .card-school {
        font-family: 'Cinzel', serif;
        font-size: 10.5px;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #c9a84c;
        margin-bottom: 14px;
        opacity: 0.75;
    }

    .card-verdict {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        font-size: 1.08rem;
        color: #d4c8b0;
        margin-bottom: 14px;
        line-height: 1.45;
        padding-left: 14px;
        border-left: 2px solid rgba(201,168,76,0.35);
    }

    .card-reasoning {
        font-size: 0.9rem;
        color: #5a5040;
        line-height: 1.7;
        margin-bottom: 16px;
        font-family: 'EB Garamond', serif;
    }

    .card-principle {
        font-size: 10px;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        color: rgba(201,168,76,0.4);
        border-top: 1px solid rgba(201,168,76,0.1);
        padding-top: 14px;
        font-style: italic;
        font-family: 'EB Garamond', serif;
    }

    /* ─── Synthesis Block ───────────────────────────── */
    .synthesis-box {
        background: rgba(255,255,255,0.018);
        border: 1px solid rgba(201,168,76,0.14);
        border-radius: 22px;
        padding: 40px 44px;
        position: relative;
        overflow: hidden;
        margin-top: 8px;
    }
    .synthesis-box::before {
        content: '"';
        position: absolute;
        top: -30px; left: 24px;
        font-family: 'EB Garamond', serif;
        font-size: 220px;
        color: rgba(201,168,76,0.045);
        line-height: 1;
        pointer-events: none;
        user-select: none;
    }

    .synthesis-label {
        font-family: 'Cinzel', serif;
        font-size: 10px;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #c9a84c;
        opacity: 0.55;
        margin-bottom: 18px;
    }

    .synthesis-text {
        font-family: 'EB Garamond', serif;
        font-size: 1.12rem;
        line-height: 1.8;
        color: #a89880;
        margin-bottom: 28px;
        position: relative;
    }

    .tag-group-label {
        font-family: 'Cinzel', serif;
        font-size: 9.5px;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #5a5040;
        margin-bottom: 10px;
    }

    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
    }

    .tag-agree {
        padding: 6px 16px;
        background: rgba(26, 90, 74, 0.2);
        border: 1px solid rgba(26, 90, 74, 0.35);
        border-radius: 24px;
        font-size: 12.5px;
        color: #6aaa8a;
        font-style: italic;
        font-family: 'EB Garamond', serif;
        transition: background 0.2s;
    }
    .tag-agree:hover { background: rgba(26, 90, 74, 0.32); }

    .tag-conflict {
        padding: 6px 16px;
        background: rgba(100, 30, 30, 0.2);
        border: 1px solid rgba(120, 40, 40, 0.32);
        border-radius: 24px;
        font-size: 12.5px;
        color: #aa6a6a;
        font-style: italic;
        font-family: 'EB Garamond', serif;
        transition: background 0.2s;
    }
    .tag-conflict:hover { background: rgba(100, 30, 30, 0.32); }

    /* ─── Spinner & Error ───────────────────────────── */
    .stSpinner > div {
        border-color: #c9a84c !important;
        border-top-color: transparent !important;
    }

    div[data-testid="stAlert"] {
        background: rgba(100, 30, 30, 0.2) !important;
        border: 1px solid rgba(120, 40, 40, 0.35) !important;
        border-radius: 10px !important;
        color: #aa6a6a !important;
        font-family: 'EB Garamond', serif !important;
    }

    /* ─── Footer ─────────────────────────────────────── */
    .page-footer {
        text-align: center;
        margin-top: 70px;
        padding-top: 24px;
        border-top: 1px solid rgba(201,168,76,0.08);
    }
    .footer-text {
        font-family: 'EB Garamond', serif;
        font-style: italic;
        font-size: 0.82rem;
        color: #3a3020;
        letter-spacing: 1px;
    }

    /* ─── Streamlit columns gap ─────────────────────── */
    [data-testid="stHorizontalBlock"] { gap: 20px !important; }

    /* ─── Caption override ──────────────────────────── */
    .stCaption { color: #4a4030 !important; font-family: 'EB Garamond', serif !important; }
    [data-testid="stCaption"] { color: #4a4030 !important; }

    /* Remove label from text area */
    .stTextArea label { display: none !important; }

    /* Multiselect label */
    .stMultiSelect label {
        font-family: 'Cinzel', serif !important;
        font-size: 10px !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: #c9a84c !important;
        opacity: 0.6 !important;
    }

    /* hr override */
    hr { border-color: rgba(201,168,76,0.12) !important; margin: 40px 0 !important; }
</style>

<!-- Animated background -->
<div class="bg-canvas" aria-hidden="true">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
  <div class="orb orb4"></div>
</div>
""", unsafe_allow_html=True)


# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="eyebrow">Philosophical Analysis Engine</div>
  <h1 class="main-title">EthosSynth</h1>
  <div class="ornament-row">
    <div class="ornament-line"></div>
    <span class="ornament-icon">⚖</span>
    <div class="ornament-line"></div>
  </div>
  <p class="subtitle">Examine your dilemma through the eyes of history's greatest ethical traditions</p>
</div>
""", unsafe_allow_html=True)


# ─── Fetch Available Philosophies ────────────────────────────────────────────
@st.cache_data
def get_philosophies():
    try:
        resp = requests.get(f"{API_BASE}/philosophies", timeout=10)
        resp.raise_for_status()
        return resp.json()["schools"]
    except Exception:
        return [
            {"id": "utilitarian",    "name": "Utilitarian",             "tagline": "Greatest good for the greatest number"},
            {"id": "kantian",        "name": "Kantian (Deontological)", "tagline": "Duty, rules, and universal principles"},
            {"id": "stoic",          "name": "Stoic",                   "tagline": "Focus on what you control; virtue above all"},
            {"id": "virtue_ethics",  "name": "Virtue Ethics",           "tagline": "What would a person of good character do?"},
            {"id": "existentialist", "name": "Existentialist",          "tagline": "Radical freedom; you define your own meaning"},
            {"id": "care_ethics",    "name": "Care Ethics",             "tagline": "Relationships and context matter most"},
            {"id": "social_contract","name": "Social Contract",         "tagline": "What rules would rational people agree to?"},
            {"id": "buddhist",       "name": "Buddhist Ethics",         "tagline": "Reduce suffering; practice non-attachment"},
        ]


philosophies   = get_philosophies()
philosophy_names = [p["name"] for p in philosophies]
philosophy_map   = {p["name"]: p["tagline"] for p in philosophies}


# ─── Input Area ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<div class="panel"><div class="panel-label">Describe your dilemma</div>', unsafe_allow_html=True)
    dilemma = st.text_area(
        label="dilemma_input",
        label_visibility="collapsed",
        placeholder=(
            "e.g. I discovered my close friend has been lying to their partner for months. "
            "They asked me to keep it secret. Should I tell their partner?"
        ),
        height=190,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="panel"><div class="panel-label">Choose your philosophical lenses</div>', unsafe_allow_html=True)
    for name, tagline in philosophy_map.items():
        st.caption(f"**{name}** — *{tagline}*")
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Philosophy Selector ─────────────────────────────────────────────────────
selected = st.multiselect(
    label="APPLY LENSES — SELECT 2 TO 5",
    options=philosophy_names,
    default=["Utilitarian", "Kantian (Deontological)", "Stoic"],
    max_selections=5,
)


# ─── Analyze Button ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("⚖  Consult the Philosophers", type="primary", use_container_width=True)


# ─── Results ─────────────────────────────────────────────────────────────────
ROMAN = ["I", "II", "III", "IV", "V"]

if analyze_btn:
    if not dilemma.strip() or len(dilemma.strip()) < 20:
        st.error("Please describe your dilemma in at least a sentence or two.")
    elif len(selected) < 2:
        st.error("Please select at least 2 philosophical schools.")
    else:
        with st.spinner("Consulting the philosophers… this may take 20–40 seconds."):
            try:
                resp = requests.post(
                    f"{API_BASE}/analyze",
                    json={"dilemma": dilemma, "philosophies": selected},
                    timeout=120,
                )
                resp.raise_for_status()
                result = resp.json()

                # Section divider
                st.markdown("""
                <div class="section-divider">
                  <div class="section-divider-line"></div>
                  <span class="section-divider-label">Philosophical Analyses</span>
                  <div class="section-divider-line"></div>
                </div>
                """, unsafe_allow_html=True)

                # Philosophy cards — up to 3 per row
                analyses = result["analyses"]
                for row_start in range(0, len(analyses), 3):
                    row = analyses[row_start : row_start + 3]
                    cols = st.columns(len(row), gap="medium")
                    for i, (col, analysis) in enumerate(zip(cols, row)):
                        idx = row_start + i
                        numeral = ROMAN[idx] if idx < len(ROMAN) else str(idx + 1)
                        with col:
                            st.markdown(f"""
                            <div class="philosophy-card">
                                <div class="card-index">{numeral}</div>
                                <div class="card-school">{analysis['school']}</div>
                                <div class="card-verdict">"{analysis['verdict']}"</div>
                                <div class="card-reasoning">{analysis['reasoning']}</div>
                                <div class="card-principle">{analysis['key_principle']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                # Synthesis
                if result.get("synthesis"):
                    st.markdown("""
                    <div class="section-divider" style="margin-top:44px;">
                      <div class="section-divider-line"></div>
                      <span class="section-divider-label">Synthesis</span>
                      <div class="section-divider-line"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    agree_tags = "".join(
                        f'<span class="tag-agree">✦ {a}</span>'
                        for a in result.get("areas_of_agreement", [])
                    )
                    conflict_tags = "".join(
                        f'<span class="tag-conflict">✗ {c}</span>'
                        for c in result.get("areas_of_conflict", [])
                    )

                    agree_section = (
                        f'<div class="tag-group-label">Where they agree</div>'
                        f'<div class="tag-row">{agree_tags}</div>'
                    ) if agree_tags else ""

                    conflict_section = (
                        f'<div class="tag-group-label" style="margin-top:6px;">Where they clash</div>'
                        f'<div class="tag-row">{conflict_tags}</div>'
                    ) if conflict_tags else ""

                    synthesis_html = (
                        f'<div class="synthesis-box">'
                        f'<div class="synthesis-label">Synthesis</div>'
                        f'<p class="synthesis-text">{result["synthesis"]}</p>'
                        f'{agree_section}'
                        f'{conflict_section}'
                        f'</div>'
                    )
                    st.markdown(synthesis_html, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the API backend. "
                    "Make sure FastAPI is running (`uvicorn app.main:app --reload`)."
                )
            except requests.exceptions.Timeout:
                st.error("The analysis timed out. The model may be loading — try again in 30 seconds.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-footer">
  <p class="footer-text"></p>
</div>
""", unsafe_allow_html=True)