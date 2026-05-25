import streamlit as st
import joblib
import plotly.graph_objects as go
import numpy as np
import re
import string
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FakeShield · AI News Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Shared CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Syne:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background: #0e0618;
    color: #e8d9f5;
}
[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(180,120,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(180,120,255,0.04) 1px, transparent 1px),
        radial-gradient(ellipse at 15% 60%, rgba(100,30,180,0.30) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(160,80,0,0.22) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 90%, rgba(120,40,200,0.18) 0%, transparent 60%),
        #0e0618;
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100%, 100% 100%;
}
[data-testid="stHeader"] { background: transparent; }
/* ── Hide sidebar toggle & sidebar entirely ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── Top navbar ── */
.topnav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(14,6,24,0.92);
    border-bottom: 1px solid rgba(180,120,255,0.18);
    backdrop-filter: blur(16px);
    padding: .65rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 4px 32px rgba(100,30,180,0.18);
}
.topnav-brand {
    font-family: "Orbitron", monospace;
    font-size: 1rem;
    font-weight: 900;
    letter-spacing: .18em;
    background: linear-gradient(135deg, #ffd700, #c97bff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    white-space: nowrap;
}
.topnav-links {
    display: flex;
    gap: .4rem;
    align-items: center;
}
.topnav-pill {
    font-family: "Orbitron", monospace;
    font-size: .6rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    padding: .45rem 1.1rem;
    border-radius: 999px;
    border: 1px solid rgba(180,120,255,0.22);
    color: #9b72cf;
    background: transparent;
    cursor: pointer;
    transition: all .2s;
    text-decoration: none;
    white-space: nowrap;
}
.topnav-pill:hover { background: rgba(180,100,255,0.12); color: #e0b8ff; }
.topnav-pill-active {
    background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(180,100,255,0.15));
    border-color: rgba(255,215,0,0.45);
    color: #ffd700 !important;
    box-shadow: 0 0 14px rgba(255,215,0,0.15);
}
.topnav-badge {
    font-family: "Orbitron", monospace;
    font-size: .52rem;
    letter-spacing: .12em;
    color: #5a3a7a;
    white-space: nowrap;
}
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 900;
    letter-spacing: .14em;
    text-align: center;
    background: linear-gradient(135deg, #ffd700 0%, #ffaa00 40%, #c97bff 80%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; padding: 0;
    line-height: 1.15;
    filter: drop-shadow(0 0 32px rgba(200,140,255,0.35));
}
.hero-sub {
    text-align: center;
    font-size: 1rem;
    letter-spacing: .3em;
    text-transform: uppercase;
    color: #c4a0e8;
    margin-top: .5rem;
    margin-bottom: 1.8rem;
    text-shadow: 0 0 20px rgba(180,100,255,0.4);
}
.glass-card {
    background: rgba(20,8,40,0.78);
    border: 1px solid rgba(180,120,255,0.18);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 40px rgba(160,80,255,0.06), inset 0 1px 0 rgba(255,215,0,0.06);
    margin-bottom: 1.5rem;
}
.section-label {
    font-family: 'Orbitron', monospace;
    font-size: .68rem;
    letter-spacing: .3em;
    text-transform: uppercase;
    color: #c97bff;
    margin-bottom: .7rem;
}
.page-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 700;
    letter-spacing: .12em;
    color: #ffd700;
    margin-bottom: .3rem;
}
.page-divider {
    height: 2px;
    background: linear-gradient(90deg, #ffd700, #c97bff, transparent);
    border: none;
    margin: .4rem 0 2rem;
    border-radius: 2px;
}
textarea {
    background: rgba(0,20,40,0.8) !important;
    border: 1px solid rgba(180,120,255,0.25) !important;
    border-radius: 10px !important;
    color: #c9d8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: .95rem !important;
    caret-color: #ffd700;
}
textarea:focus {
    border-color: rgba(200,140,255,0.7) !important;
    box-shadow: 0 0 0 2px rgba(180,100,255,0.18) !important;
}
.stButton > button {
    width: 100%;
    padding: .85rem 1.4rem;
    font-family: 'Orbitron', monospace;
    font-weight: 600;
    font-size: .8rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #050a12 !important;
    background: linear-gradient(135deg, #ffd700, #c97bff) !important;
    border: none !important;
    border-radius: 10px !important;
    cursor: pointer;
    transition: all .25s ease;
    box-shadow: 0 0 24px rgba(200,140,255,0.35);
}
.stButton > button:hover {
    box-shadow: 0 0 40px rgba(220,160,255,0.6);
    transform: translateY(-2px);
}
.verdict-real {
    background: linear-gradient(135deg, rgba(0,255,170,0.12), rgba(0,200,120,0.05));
    border: 1px solid rgba(0,255,170,0.35);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    text-align: center;
}
.verdict-fake {
    background: linear-gradient(135deg, rgba(255,50,80,0.12), rgba(200,0,50,0.05));
    border: 1px solid rgba(255,50,80,0.35);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    text-align: center;
}
.verdict-text {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.2rem, 3vw, 2rem);
    font-weight: 900;
    letter-spacing: .14em;
}
.verdict-text-real { color: #00ffaa; }
.verdict-text-fake { color: #ff3250; }
.stat-tile {
    background: rgba(0,20,45,0.7);
    border: 1px solid rgba(180,120,255,0.12);
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
}
.stat-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffd700;
    line-height: 1;
}
.stat-label {
    font-size: .68rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #9b72cf;
    margin-top: .35rem;
}
.history-badge {
    font-family: 'Orbitron', monospace;
    font-size: .6rem;
    font-weight: 700;
    letter-spacing: .15em;
    padding: .25rem .7rem;
    border-radius: 6px;
    white-space: nowrap;
}
.badge-real { background: rgba(0,255,170,0.15); color: #00ffaa; border: 1px solid rgba(0,255,170,0.3); }
.badge-fake { background: rgba(255,50,80,0.15);  color: #ff3250; border: 1px solid rgba(255,50,80,0.3); }
.model-badge {
    display: inline-block;
    font-family: 'Orbitron', monospace;
    font-size: .58rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: #c97bff;
    background: rgba(160,80,255,0.10);
    border: 1px solid rgba(200,140,255,0.22);
    border-radius: 6px;
    padding: .25rem .7rem;
    margin-bottom: 1.5rem;
}
.info-tile {
    background: rgba(20,8,40,0.65);
    border: 1px solid rgba(180,120,255,0.15);
    border-radius: 14px;
    padding: 1.6rem 1.4rem;
    height: 100%;
}
.info-tile-icon  { font-size: 2rem; margin-bottom: .7rem; display: block; }
.info-tile-title {
    font-family: 'Orbitron', monospace;
    font-size: .72rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: #ffd700;
    margin-bottom: .5rem;
}
.info-tile-body  { font-size: .88rem; color: #b8a0d0; line-height: 1.6; }
.tech-pill {
    display: inline-block;
    font-family: 'Orbitron', monospace;
    font-size: .58rem;
    letter-spacing: .15em;
    padding: .3rem .75rem;
    border-radius: 999px;
    margin: .2rem .18rem;
    border: 1px solid rgba(200,140,255,0.25);
    background: rgba(140,60,220,0.12);
    color: #c97bff;
}
.footer {
    text-align: center;
    font-size: .68rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: #3a1a5a;
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(180,100,255,0.10);
}
.js-plotly-plot, .plotly, .plot-container { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_models():
    vectorizer = joblib.load("vectorizer.jb")
    model      = joblib.load("lr_model.jb")
    return vectorizer, model


def text_stats(text: str) -> dict:
    words  = text.split()
    sents  = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    unique = set(w.lower().strip(string.punctuation) for w in words)
    return {
        "words":        len(words),
        "chars":        len(text),
        "sentences":    len(sents),
        "unique_words": len(unique),
        "avg_word_len": round(np.mean([len(w) for w in words]), 1) if words else 0,
    }


def gauge_chart(confidence: float, label: str, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        number={"suffix": "%", "font": {"size": 30, "color": color,
                                        "family": "Orbitron, monospace"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#2a1040",
                     "tickfont": {"color": "#5a3a7a", "size": 9}},
            "bar": {"color": color, "thickness": 0.26},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  33], "color": "rgba(255,50,80,0.10)"},
                {"range": [33, 66], "color": "rgba(255,200,0,0.07)"},
                {"range": [66,100], "color": "rgba(0,255,170,0.08)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.80,
                "value": confidence * 100,
            },
        },
        title={"text": label, "font": {"size": 10, "color": "#7a5a9a",
                                       "family": "Orbitron, monospace"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=28, b=8, l=18, r=18), height=210,
    )
    return fig


def prob_bar(prob_fake: float, prob_real: float):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[prob_fake * 100], y=[""], orientation="h",
        marker_color="rgba(255,50,80,0.75)",
        marker_line_color="rgba(255,50,80,1)", marker_line_width=1.5,
        name="Fake", text=f"  FAKE  {prob_fake*100:.1f}%",
        textposition="inside",
        textfont=dict(color="white", size=11, family="Orbitron, monospace"),
        width=0.45,
    ))
    fig.add_trace(go.Bar(
        x=[prob_real * 100], y=[""], orientation="h",
        marker_color="rgba(0,255,170,0.70)",
        marker_line_color="rgba(0,255,170,1)", marker_line_width=1.5,
        name="Real", text=f"  REAL  {prob_real*100:.1f}%",
        textposition="inside",
        textfont=dict(color="#050a12", size=11, family="Orbitron, monospace"),
        width=0.45,
    ))
    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=8, b=8, l=8, r=8), height=80,
        xaxis=dict(range=[0,100], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        showlegend=False,
    )
    return fig


def radar_chart(stats: dict):
    cats = ["Word Count", "Sent. Count", "Unique Words", "Avg Word Len", "Char Density"]
    vals = [
        min(stats["words"] / 10, 100),
        min(stats["sentences"] * 5, 100),
        min(stats["unique_words"] / 8, 100),
        min(stats["avg_word_len"] * 10, 100),
        min(stats["chars"] / 20, 100),
    ]
    vals += [vals[0]]
    cats += [cats[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(200,120,255,0.08)",
        line=dict(color="rgba(200,120,255,0.6)", width=2),
        marker=dict(size=5, color="#c97bff"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], showticklabels=False,
                            gridcolor="rgba(180,100,255,0.10)",
                            linecolor="rgba(180,100,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(180,100,255,0.10)",
                             linecolor="rgba(180,100,255,0.15)",
                             tickfont=dict(color="#7a5a9a", size=9,
                                          family="Syne, sans-serif")),
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=18, b=18, l=28, r=28), height=250,
        showlegend=False,
    )
    return fig


def ensure_history():
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []


def add_to_history(article, label, confidence, prob_real, prob_fake, stats):
    ensure_history()
    st.session_state.prediction_history.insert(0, {
        "timestamp":  datetime.now().strftime("%H:%M:%S"),
        "date":       datetime.now().strftime("%d %b %Y"),
        "snippet":    article[:120].replace("\n", " "),
        "label":      label,
        "confidence": confidence,
        "prob_real":  prob_real,
        "prob_fake":  prob_fake,
        "stats":      stats,
        "full_text":  article,
    })


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
ensure_history()

# ── Navbar rendered via query-param routing ──────────────────────────────────
PAGES = ["🏠  Home", "🔍  Prediction", "📜  History"]

# Read current page from query params (default = Home)
qp = st.query_params
if "page" not in qp:
    qp["page"] = "home"

_slug_map = {"home": "🏠  Home", "prediction": "🔍  Prediction", "history": "📜  History"}
_rev_map  = {"🏠  Home": "home", "🔍  Prediction": "prediction", "📜  History": "history"}
app_mode  = _slug_map.get(qp.get("page", "home"), "🏠  Home")

history_count = len(st.session_state.prediction_history)

def _pill(label, current):
    slug   = _rev_map[label]
    active = "topnav-pill-active" if label == current else ""
    icon   = label.split("  ")[0]
    name   = label.split("  ")[1]
    # badge count on history pill
    badge  = f' <span style="opacity:.6;font-size:.5rem">({history_count})</span>' if "History" in name else ""
    return (f'<a href="?page={slug}" target="_self" ' 
            f'class="topnav-pill {active}">{icon} {name}{badge}</a>')

pills_html = "".join(_pill(p, app_mode) for p in PAGES)

st.markdown(f'''
<nav class="topnav">
    <div class="topnav-brand">🛡&nbsp; FAKESHIELD</div>
    <div class="topnav-links">{pills_html}</div>
    <div class="topnav-badge">📜 {history_count} prediction{"s" if history_count != 1 else ""} this session</div>
</nav>
''', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if app_mode == "🏠  Home":

    st.markdown('<p class="hero-title">🛡 FAKESHIELD</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">AI-Powered News Authenticity Detection</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin-bottom:2rem">'
        '<span class="model-badge">'
        '⚙ Logistic Regression · TF-IDF Vectorizer · Trained on 44 k+ Articles'
        '</span></div>',
        unsafe_allow_html=True,
    )

    # About
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📌 About The Project</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#c4a0e8;font-size:.97rem;line-height:1.75;margin:0">
    FakeShield is an AI-powered fake news detection system that classifies news articles as
    <strong style="color:#00ffaa">Real</strong> or <strong style="color:#ff3250">Fake</strong>
    using Natural Language Processing and Machine Learning. The system analyses article text,
    extracts TF-IDF features, and applies a trained Logistic Regression model to produce a
    binary verdict backed by real-time confidence scores and interactive linguistic visualisations.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Feature tiles
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, body in [
        (c1, "🔍", "Smart Classification",
         "TF-IDF + Logistic Regression pipeline classifies any news article instantly."),
        (c2, "📊", "Confidence Scores",
         "Real-time probability estimates for both Real and Fake classes via predict_proba()."),
        (c3, "🧬", "Linguistic Fingerprint",
         "Radar chart visualises 5 linguistic dimensions: vocabulary, sentence structure & more."),
        (c4, "📜", "Prediction History",
         "Every analysis is stored in session history so you can review and compare past results."),
    ]:
        with col:
            st.markdown(f"""
            <div class="info-tile">
                <span class="info-tile-icon">{icon}</span>
                <div class="info-tile-title">{title}</div>
                <div class="info-tile-body">{body}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Model details + Tech stack
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🤖 Model Architecture</div>', unsafe_allow_html=True)
        for label, value in [
            ("Algorithm",     "Logistic Regression"),
            ("Vectorisation", "TF-IDF (Term Frequency – Inverse Document Frequency)"),
            ("Training Data", "44,000+ labelled news articles"),
            ("Classes",       "Real News (1)  ·  Fake News (0)"),
            ("Test Accuracy", "~98 – 99 %"),
            ("Confidence",    "Extracted via predict_proba()"),
            ("Artifacts",     "vectorizer.jb  +  lr_model.jb"),
        ]:
            st.markdown(f"""
            <div style="display:flex;gap:.8rem;align-items:flex-start;
                        border-bottom:1px solid rgba(180,120,255,0.08);padding:.55rem 0">
                <span style="font-family:'Orbitron',monospace;font-size:.58rem;
                              letter-spacing:.15em;text-transform:uppercase;
                              color:#c97bff;min-width:125px;padding-top:2px">{label}</span>
                <span style="color:#e8d9f5;font-size:.87rem">{value}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🛠 Tech Stack</div>', unsafe_allow_html=True)
        for cat, pills in {
            "Machine Learning": ["Scikit-learn", "Logistic Regression", "TF-IDF", "Joblib"],
            "NLP":              ["Python re", "NLTK", "String ops", "NumPy"],
            "Visualisation":    ["Plotly", "Gauge Charts", "Radar Chart", "Bar Chart"],
            "Frontend":         ["Streamlit", "Custom CSS", "Orbitron Font", "Glassmorphism"],
            "Deployment":       ["Streamlit Cloud", "Session State", "requirements.txt"],
        }.items():
            st.markdown(
                f"<div style='margin-bottom:.9rem'>"
                f"<div style='font-family:Orbitron,monospace;font-size:.58rem;"
                f"letter-spacing:.2em;text-transform:uppercase;color:#ffd700;"
                f"margin-bottom:.35rem'>{cat}</div>"
                f"<div>{''.join(f'<span class=\"tech-pill\">{p}</span>' for p in pills)}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">⚡ How It Works</div>', unsafe_allow_html=True)
    hw_cols = st.columns(3)
    for i, (num, color, title, body) in enumerate([
        ("01", "#ffd700", "Paste Article",      "Enter any news article — headline, body, or both — into the Prediction page."),
        ("02", "#c97bff", "TF-IDF Transform",   "The saved vectoriser converts text into a high-dimensional feature vector."),
        ("03", "#00ffaa", "LR Classification",  "The Logistic Regression model predicts Real or Fake from the feature vector."),
        ("04", "#ff9020", "Confidence Scores",  "predict_proba() extracts probability estimates for both classes."),
        ("05", "#00c8ff", "Visual Analysis",    "Results render as gauge charts, probability bar, radar chart, and stat tiles."),
        ("06", "#ff3250", "History Saved",      "Every prediction is automatically logged to the History page for review."),
    ]):
        with hw_cols[i % 3]:
            st.markdown(f"""
            <div style="display:flex;gap:.9rem;align-items:flex-start;margin-bottom:1.2rem">
                <span style="font-family:'Orbitron',monospace;font-size:1.3rem;
                              font-weight:900;color:{color};opacity:.5;
                              line-height:1;min-width:34px">{num}</span>
                <div>
                    <div style="font-family:'Orbitron',monospace;font-size:.63rem;
                                  letter-spacing:.15em;text-transform:uppercase;
                                  color:{color};margin-bottom:.3rem">{title}</div>
                    <div style="font-size:.82rem;color:#9b72cf;line-height:1.55">{body}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Confidence guide
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📖 Reading Confidence Scores</div>', unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    for col, color, pct, label, desc in [
        (b1, "#00ffaa", "≥ 80 %",    "High Certainty",     "Strong match with training data. High reliability verdict."),
        (b2, "#ffd700", "60 – 80 %", "Moderate Certainty", "Reasonable confidence. Cross-check with trusted sources."),
        (b3, "#ff3250", "< 60 %",    "Low Certainty",      "Ambiguous content — satire, opinion, or domain mismatch."),
    ]:
        with col:
            st.markdown(f"""
            <div style="border:1px solid {color}30;border-radius:12px;
                        padding:1.1rem;background:{color}08">
                <div style="font-family:'Orbitron',monospace;font-size:1.3rem;
                              font-weight:700;color:{color}">{pct}</div>
                <div style="font-family:'Orbitron',monospace;font-size:.6rem;
                              letter-spacing:.15em;text-transform:uppercase;
                              color:{color};opacity:.8;margin:.3rem 0">{label}</div>
                <div style="font-size:.82rem;color:#9b72cf;line-height:1.5">{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin:2rem 0 1rem">
        <div style="font-size:.85rem;color:#5a3a7a">
            Use the <strong style="color:#ffd700">navbar</strong> above to navigate to
            <strong style="color:#c97bff">Prediction</strong> or
            <strong style="color:#c97bff">History</strong>.
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="footer">FakeShield · Built with Streamlit · Logistic Regression + TF-IDF</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
elif app_mode == "🔍  Prediction":

    vectorizer, model = load_models()

    st.markdown('<p class="page-title">🔍 News Prediction</p>', unsafe_allow_html=True)
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin-bottom:1.6rem">'
        '<span class="model-badge">⚙ Logistic Regression · TF-IDF Vectorizer · 44 k+ Articles</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Initialise buffer (separate from widget — avoids StreamlitAPIException) ──
    if "_article_text" not in st.session_state:
        st.session_state["_article_text"] = ""

    # Input card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📰 Article Input</div>', unsafe_allow_html=True)

    # value= (not key=) so we can freely write to _article_text at any point
    article = st.text_area(
        label="",
        placeholder="Paste a news article here — headline, body text, or both…",
        height=230,
        label_visibility="collapsed",
        value=st.session_state["_article_text"],
    )
    # Keep buffer in sync with whatever the user typed
    st.session_state["_article_text"] = article

    btn_col, clr_col = st.columns([3, 1])
    with btn_col:
        analyze = st.button("⚡  ANALYZE ARTICLE")
    with clr_col:
        if st.button("✕  Clear"):
            st.session_state["_article_text"] = ""
            st.rerun()

    if article.strip():
        wc = len(article.split())
        st.markdown(
            f"<div style='font-size:.72rem;color:#5a3a7a;text-align:right;margin-top:.3rem'>"
            f"{wc} word{'s' if wc != 1 else ''}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Sample articles loader
    with st.expander("💡  Load a sample article to test"):
        samples = {
            "Reuters — Real Article": (
                "WASHINGTON (Reuters) - The U.S. Federal Reserve held interest rates steady "
                "on Wednesday and signalled it was in no hurry to resume cutting them, as "
                "officials pointed to solid economic growth and a still-healthy labour market "
                "while awaiting more clarity on the potential economic impact of policies."
            ),
            "Fabricated — Fake Article": (
                "BREAKING: Scientists confirm that drinking bleach once per week boosts "
                "immunity by 400%. The government is hiding this because Big Pharma doesn't "
                "want you to know. Share before they delete this! Thousands are already doing "
                "this and reporting miraculous recoveries."
            ),
            "Political — Borderline": (
                "President announces sweeping tax reform that will eliminate the middle class. "
                "Sources say the plan was drafted in secret by billionaires and will transfer "
                "trillions from ordinary Americans to the ultra-wealthy. Congress is expected "
                "to vote without reading the bill."
            ),
        }
        choice = st.selectbox("Select a sample", list(samples.keys()),
                              label_visibility="collapsed")
        if st.button("📋  Load Sample"):
            # Safe: _article_text is NOT the widget key, so Streamlit allows this
            st.session_state["_article_text"] = samples[choice]
            st.rerun()

    # ── Analysis ──────────────────────────────────────────────────────────────
    if analyze:
        if not article.strip():
            st.warning("⚠ Please enter some article text before scanning.")
        else:
            vec        = vectorizer.transform([article])
            proba      = model.predict_proba(vec)[0]
            pred       = model.predict(vec)[0]
            prob_fake, prob_real = proba[0], proba[1]
            is_real    = (pred == 1)
            confidence = prob_real if is_real else prob_fake
            label      = "REAL" if is_real else "FAKE"

            stats = text_stats(article)
            add_to_history(article, label, confidence, prob_real, prob_fake, stats)

            # Verdict banner
            if is_real:
                st.markdown(f"""
                <div class="verdict-real">
                    <div class="verdict-text verdict-text-real">✔ AUTHENTIC NEWS</div>
                    <div style="color:#4adfaa;font-size:.9rem;margin-top:.5rem;letter-spacing:.08em">
                        Model confidence: <strong>{confidence*100:.1f}%</strong>
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="verdict-fake">
                    <div class="verdict-text verdict-text-fake">✗ FAKE NEWS DETECTED</div>
                    <div style="color:#ff6080;font-size:.9rem;margin-top:.5rem;letter-spacing:.08em">
                        Model confidence: <strong>{confidence*100:.1f}%</strong>
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Gauges + prob bar + radar
            col1, col2, col3 = st.columns([1, 1, 1.15])
            with col1:
                st.markdown('<div class="glass-card" style="padding:1.2rem 1rem">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Real Probability</div>', unsafe_allow_html=True)
                st.plotly_chart(gauge_chart(prob_real, "Real News Score", "#00ffaa"),
                                use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="glass-card" style="padding:1.2rem 1rem">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Fake Probability</div>', unsafe_allow_html=True)
                st.plotly_chart(gauge_chart(prob_fake, "Fake News Score", "#ff3250"),
                                use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="glass-card" style="padding:1.2rem 1rem">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Probability Split</div>', unsafe_allow_html=True)
                st.plotly_chart(prob_bar(prob_fake, prob_real),
                                use_container_width=True, config={"displayModeBar": False})
                st.markdown('<div class="section-label" style="margin-top:1rem">Linguistic Fingerprint</div>',
                            unsafe_allow_html=True)
                st.plotly_chart(radar_chart(stats),
                                use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            # Stats tiles
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">📊 Article Statistics</div>', unsafe_allow_html=True)
            s1, s2, s3, s4, s5 = st.columns(5)
            for col, val, lbl in [
                (s1, str(stats["words"]),        "Words"),
                (s2, str(stats["sentences"]),    "Sentences"),
                (s3, str(stats["unique_words"]), "Unique Words"),
                (s4, str(stats["avg_word_len"]), "Avg Word Len"),
                (s5, str(stats["chars"]),        "Characters"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="stat-tile">
                        <div class="stat-value">{val}</div>
                        <div class="stat-label">{lbl}</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Model info
            with st.expander("ℹ  Model Details & Interpretation"):
                st.markdown("""
**Model:** Logistic Regression with TF-IDF vectorization  
**Training data:** ~44,000 articles (Fake.csv + True.csv dataset)  
**Test-set accuracy:** ~98 – 99 %

**How to read the scores:**
- **Confidence ≥ 80 %** → High certainty verdict
- **Confidence 60 – 80 %** → Moderate certainty; cross-check with other sources
- **Confidence < 60 %** → Low certainty; treat as inconclusive

**Limitations:** Trained on English-language news. May not generalise to satire,
opinion pieces, or non-English content.
                """)

            total_h = len(st.session_state.prediction_history)
            st.markdown(
                f"<div style='text-align:center;margin-top:1rem'>"
                f"<span style='font-size:.8rem;color:#5a3a7a'>✓ Saved to "
                f"<strong style='color:#c97bff'>History</strong> "
                f"({total_h} total this session)</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="footer">FakeShield · Prediction · Logistic Regression + TF-IDF</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif app_mode == "📜  History":

    st.markdown('<p class="page-title">📜 Prediction History</p>', unsafe_allow_html=True)
    st.markdown('<hr class="page-divider">', unsafe_allow_html=True)

    history = st.session_state.prediction_history

    # Empty state
    if not history:
        st.markdown("""
        <div style="text-align:center;padding:5rem 2rem">
            <div style="font-size:4rem;margin-bottom:1rem">🔍</div>
            <div style="font-family:'Orbitron',monospace;font-size:.9rem;
                        letter-spacing:.2em;text-transform:uppercase;color:#5a3a7a">
                No predictions yet
            </div>
            <div style="font-size:.85rem;color:#5a3a7a;margin-top:.5rem">
                Go to <strong style="color:#ffd700">Prediction</strong> in the navbar above
                and analyse your first article.
            </div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # Summary bar
    total    = len(history)
    real_cnt = sum(1 for h in history if h["label"] == "REAL")
    fake_cnt = total - real_cnt
    avg_conf = sum(h["confidence"] for h in history) / total

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📊 Session Summary</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, str(total),              "Total Analyses"),
        (m2, str(real_cnt),           "Real News"),
        (m3, str(fake_cnt),           "Fake News"),
        (m4, f"{avg_conf*100:.1f}%",  "Avg Confidence"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-tile">
                <div class="stat-value">{val}</div>
                <div class="stat-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Charts row
    if total > 1:
        dc1, dc2 = st.columns([1, 2])
        with dc1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Verdict Distribution</div>', unsafe_allow_html=True)
            donut = go.Figure(go.Pie(
                labels=["Real News", "Fake News"],
                values=[real_cnt, fake_cnt],
                hole=0.62,
                marker_colors=["rgba(0,255,170,0.75)", "rgba(255,50,80,0.75)"],
                textfont=dict(family="Orbitron, monospace", size=10),
                textinfo="label+percent",
            ))
            donut.update_traces(marker_line_color="#0e0618", marker_line_width=2)
            donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10), height=220,
                showlegend=False,
                annotations=[dict(
                    text=f"<b>{total}</b>", x=0.5, y=0.5,
                    font_size=18, font_family="Orbitron, monospace",
                    font_color="#ffd700", showarrow=False,
                )],
            )
            st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with dc2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Confidence Timeline</div>', unsafe_allow_html=True)
            confs  = [h["confidence"] * 100 for h in reversed(history)]
            labels = [h["label"] for h in reversed(history)]
            colors = ["rgba(0,255,170,0.8)" if l == "REAL"
                      else "rgba(255,50,80,0.8)" for l in labels]
            line_fig = go.Figure()
            line_fig.add_trace(go.Scatter(
                y=confs, mode="lines+markers",
                line=dict(color="rgba(180,120,255,0.5)", width=1.5),
                marker=dict(color=colors, size=9, line=dict(width=1.5, color="#0e0618")),
                hovertemplate="<b>%{text}</b><br>Confidence: %{y:.1f}%<extra></extra>",
                text=labels,
            ))
            line_fig.add_hline(y=80, line_dash="dot",
                               line_color="rgba(0,255,170,0.2)", line_width=1)
            line_fig.add_hline(y=60, line_dash="dot",
                               line_color="rgba(255,215,0,0.2)", line_width=1)
            line_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10), height=220,
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(range=[0, 105], showgrid=True,
                           gridcolor="rgba(180,100,255,0.08)",
                           tickfont=dict(color="#5a3a7a", size=9), zeroline=False),
                showlegend=False,
            )
            st.plotly_chart(line_fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    # Filter controls
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">🔎 Filter & Search</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        search_q = st.text_input("Search", placeholder="Search article text…",
                                 label_visibility="collapsed")
    with fc2:
        verdict_filter = st.selectbox("Verdict", ["All", "REAL", "FAKE"],
                                      label_visibility="collapsed")
    with fc3:
        sort_by = st.selectbox("Sort", ["Newest first", "Oldest first",
                                        "Highest confidence", "Lowest confidence"],
                               label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    filtered = history[:]
    if search_q:
        filtered = [h for h in filtered if search_q.lower() in h["snippet"].lower()]
    if verdict_filter != "All":
        filtered = [h for h in filtered if h["label"] == verdict_filter]
    if sort_by == "Oldest first":
        filtered = list(reversed(filtered))
    elif sort_by == "Highest confidence":
        filtered = sorted(filtered, key=lambda x: x["confidence"], reverse=True)
    elif sort_by == "Lowest confidence":
        filtered = sorted(filtered, key=lambda x: x["confidence"])

    # Count + clear
    inf_col, clr_col = st.columns([4, 1])
    with inf_col:
        st.markdown(f"<div style='color:#5a3a7a;font-size:.8rem;padding:.4rem 0'>"
                    f"Showing {len(filtered)} of {total} results</div>",
                    unsafe_allow_html=True)
    with clr_col:
        if st.button("🗑 Clear All"):
            st.session_state.prediction_history = []
            st.rerun()

    if not filtered:
        st.markdown("<div style='color:#5a3a7a;text-align:center;padding:2rem'>"
                    "No results match your filter.</div>", unsafe_allow_html=True)
        st.stop()

    # History entries
    for i, entry in enumerate(filtered):
        badge_cls    = "badge-real" if entry["label"] == "REAL" else "badge-fake"
        verdict_icon = "✔" if entry["label"] == "REAL" else "✗"
        conf_pct     = f"{entry['confidence']*100:.1f}%"

        with st.expander(
            f"{verdict_icon} [{entry['label']}]  {conf_pct}  ·  "
            f"{entry['snippet'][:65]}…  [{entry['timestamp']}]",
            expanded=(i == 0),
        ):
            tl, tr = st.columns([3, 1])
            with tl:
                st.markdown(f"""
                <div style="margin-bottom:.8rem">
                    <span class="history-badge {badge_cls}">{verdict_icon} {entry['label']} NEWS</span>
                    <span style="font-family:'Orbitron',monospace;font-size:.75rem;
                                  color:#ffd700;margin-left:.8rem">{conf_pct}</span>
                    <span style="font-size:.72rem;color:#5a3a7a;margin-left:.6rem">
                        {entry['date']} {entry['timestamp']}
                    </span>
                </div>
                <div style="font-size:.87rem;color:#b8a0d0;line-height:1.6;
                            background:rgba(0,0,0,0.2);border-radius:8px;
                            padding:.8rem 1rem;max-height:120px;overflow-y:auto">
                    {entry['full_text'][:500]}{'…' if len(entry['full_text']) > 500 else ''}
                </div>""", unsafe_allow_html=True)
            with tr:
                s = entry["stats"]
                for val, lbl in [
                    (s["words"],        "Words"),
                    (s["sentences"],    "Sentences"),
                    (s["unique_words"], "Unique Words"),
                    (s["avg_word_len"], "Avg Word Len"),
                ]:
                    st.markdown(f"""
                    <div class="stat-tile" style="padding:.55rem .6rem;margin-bottom:.4rem">
                        <div class="stat-value" style="font-size:.95rem">{val}</div>
                        <div class="stat-label">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.plotly_chart(gauge_chart(entry["prob_real"], "Real Score", "#00ffaa"),
                                use_container_width=True, config={"displayModeBar": False},
                                key=f"hist_gauge_real_{i}")
            with cc2:
                st.plotly_chart(gauge_chart(entry["prob_fake"], "Fake Score", "#ff3250"),
                                use_container_width=True, config={"displayModeBar": False},
                                key=f"hist_gauge_fake_{i}")
            with cc3:
                st.plotly_chart(prob_bar(entry["prob_fake"], entry["prob_real"]),
                                use_container_width=True, config={"displayModeBar": False},
                                key=f"hist_probbar_{i}")
                st.plotly_chart(radar_chart(entry["stats"]),
                                use_container_width=True, config={"displayModeBar": False},
                                key=f"hist_radar_{i}")

    st.markdown('<div class="footer">FakeShield · History</div>',
                unsafe_allow_html=True)
