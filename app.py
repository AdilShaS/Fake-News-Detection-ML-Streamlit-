import streamlit as st
import joblib
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import re
import string

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FakeShield · AI News Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load models ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    vectorizer = joblib.load("vectorizer.jb")
    model      = joblib.load("lr_model.jb")
    return vectorizer, model

vectorizer, model = load_models()

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Syne:wght@400;600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background: #0e0618;
    color: #e8d9f5;
}

/* ── Purple-gold grid background ── */
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

/* ── Hero title ── */
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(8.8rem, 14vw, 14rem);
    font-weight: 900;
    letter-spacing: .14em;
    text-align: center;
    background: linear-gradient(135deg, #ffd700 0%, #ffaa00 40%, #c97bff 80%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    padding: 0;
    text-shadow: none;
    line-height: 1.15;
    filter: drop-shadow(0 0 32px rgba(200,140,255,0.35));
}
.hero-sub {
    text-align: center;
    font-size: 1.1rem;
    letter-spacing: .3em;
    text-transform: uppercase;
    color: #c4a0e8;
    margin-top: .6rem;
    margin-bottom: 2.5rem;
    text-shadow: 0 0 20px rgba(180,100,255,0.4);
}

/* ── Glassmorphism card ── */
.glass-card {
    background: rgba(20, 8, 40, 0.78);
    border: 1px solid rgba(180, 120, 255, 0.18);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 40px rgba(160,80,255,0.06), inset 0 1px 0 rgba(255,215,0,0.06);
    margin-bottom: 1.5rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'Orbitron', monospace;
    font-size: .7rem;
    letter-spacing: .3em;
    text-transform: uppercase;
    color: #c97bff;
    margin-bottom: .6rem;
}

/* ── Text area override ── */
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

/* ── Primary button ── */
.stButton > button {
    width: 100%;
    padding: .9rem 1.4rem;
    font-family: 'Orbitron', monospace;
    font-weight: 600;
    font-size: .85rem;
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

/* ── Verdict banner ── */
.verdict-real {
    background: linear-gradient(135deg, rgba(0,255,170,0.12), rgba(0,200,120,0.05));
    border: 1px solid rgba(0,255,170,0.35);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    text-align: center;
}
.verdict-fake {
    background: linear-gradient(135deg, rgba(255,50,80,0.12), rgba(200,0,50,0.05));
    border: 1px solid rgba(255,50,80,0.35);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    text-align: center;
}
.verdict-text {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.4rem, 3vw, 2.2rem);
    font-weight: 900;
    letter-spacing: .14em;
}
.verdict-text-real { color: #00ffaa; }
.verdict-text-fake { color: #ff3250; }

/* ── Stat tile ── */
.stat-tile {
    background: rgba(0,20,45,0.7);
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
}
.stat-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffd700;
    line-height: 1;
}
.stat-label {
    font-size: .72rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #9b72cf;
    margin-top: .35rem;
}

/* ── Model badge ── */
.model-badge {
    display: inline-block;
    font-family: 'Orbitron', monospace;
    font-size: .6rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: #c97bff;
    background: rgba(160,80,255,0.10);
    border: 1px solid rgba(200,140,255,0.22);
    border-radius: 6px;
    padding: .25rem .7rem;
    margin-bottom: 1.5rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    font-size: .72rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: #3a1a5a;
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(180,100,255,0.10);
}

/* Plotly transparent bg */
.js-plotly-plot, .plotly, .plot-container { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def text_stats(text: str) -> dict:
    words  = text.split()
    sents  = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    unique = set(w.lower().strip(string.punctuation) for w in words)
    return {
        "words":    len(words),
        "chars":    len(text),
        "sentences": len(sents),
        "unique_words": len(unique),
        "avg_word_len": round(np.mean([len(w) for w in words]), 1) if words else 0,
    }

def gauge_chart(confidence: float, label: str, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        number={"suffix": "%", "font": {"size": 32, "color": color,
                                        "family": "Orbitron, monospace"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#1e3a55",
                     "tickfont": {"color": "#4a90b8", "size": 10}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  33], "color": "rgba(255,50,80,0.12)"},
                {"range": [33, 66], "color": "rgba(255,200,0,0.08)"},
                {"range": [66,100], "color": "rgba(0,255,170,0.10)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.82,
                "value": confidence * 100,
            },
        },
        title={"text": label,
               "font": {"size": 11, "color": "#4a90b8",
                        "family": "Orbitron, monospace"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10, l=20, r=20), height=220,
    )
    return fig

def prob_bar(prob_fake: float, prob_real: float):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[prob_fake * 100], y=[""], orientation="h",
        marker_color="rgba(255,50,80,0.75)",
        marker_line_color="rgba(255,50,80,1)", marker_line_width=1.5,
        name="Fake", text=f"  FAKE  {prob_fake*100:.1f}%",
        textposition="inside", textfont=dict(color="white", size=12, family="Orbitron, monospace"),
        width=0.45,
    ))
    fig.add_trace(go.Bar(
        x=[prob_real * 100], y=[""], orientation="h",
        marker_color="rgba(0,255,170,0.7)",
        marker_line_color="rgba(0,255,170,1)", marker_line_width=1.5,
        name="Real", text=f"  REAL  {prob_real*100:.1f}%",
        textposition="inside", textfont=dict(color="#050a12", size=12, family="Orbitron, monospace"),
        width=0.45,
    ))
    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10), height=90,
        xaxis=dict(range=[0,100], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        showlegend=False,
    )
    return fig

def radar_chart(stats: dict):
    categories = ["Word Count", "Sent. Count", "Unique Words", "Avg Word Len", "Char Density"]
    # normalise each to 0-100 for display
    values = [
        min(stats["words"] / 10, 100),
        min(stats["sentences"] * 5, 100),
        min(stats["unique_words"] / 8, 100),
        min(stats["avg_word_len"] * 10, 100),
        min(stats["chars"] / 20, 100),
    ]
    values += [values[0]]  # close the loop
    cats   = categories + [categories[0]]
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=cats, fill="toself",
        fillcolor="rgba(0,240,255,0.08)",
        line=dict(color="rgba(0,240,255,0.6)", width=2),
        marker=dict(size=6, color="#00f0ff"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], showticklabels=False,
                            gridcolor="rgba(0,240,255,0.1)", linecolor="rgba(0,240,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(0,240,255,0.1)", linecolor="rgba(0,240,255,0.15)",
                             tickfont=dict(color="#4a90b8", size=10, family="Syne, sans-serif")),
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=30, r=30), height=260,
        showlegend=False,
    )
    return fig


# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">🛡 FAKESHIELD</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">AI-Powered News Authenticity Detection</p>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center"><span class="model-badge">⚙ Logistic Regression · TF-IDF Vectorizer · Trained on 44 k+ Articles</span></div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">📰 Article Input</div>', unsafe_allow_html=True)
article = st.text_area(
    label="",
    placeholder="Paste a news article here — headline, body text, or both…",
    height=220,
    label_visibility="collapsed",
)
analyze = st.button("⚡  ANALYZE ARTICLE")
st.markdown("</div>", unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if analyze:
    if not article.strip():
        st.warning("⚠ Please enter some article text before scanning.")
    else:
        # ── Predict ──
        vec   = vectorizer.transform([article])
        proba = model.predict_proba(vec)[0]      # [P(fake), P(real)]
        pred  = model.predict(vec)[0]
        prob_fake, prob_real = proba[0], proba[1]
        is_real = pred == 1
        confidence = prob_real if is_real else prob_fake

        # ── Text stats ──
        stats = text_stats(article)

        # ── Verdict banner ──
        if is_real:
            st.markdown(f"""
            <div class="verdict-real">
                <div class="verdict-text verdict-text-real">✔ AUTHENTIC NEWS</div>
                <div style="color:#4adfaa;font-size:.9rem;margin-top:.5rem;letter-spacing:.08em;">
                    Model confidence: {confidence*100:.1f}%
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="verdict-fake">
                <div class="verdict-text verdict-text-fake">✗ FAKE NEWS DETECTED</div>
                <div style="color:#ff6080;font-size:.9rem;margin-top:.5rem;letter-spacing:.08em;">
                    Model confidence: {confidence*100:.1f}%
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 1: gauges + probability bar ──────────────────────────────────
        col1, col2, col3 = st.columns([1, 1, 1.1])

        with col1:
            st.markdown('<div class="glass-card" style="padding:1.2rem 1rem;">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Real Probability</div>', unsafe_allow_html=True)
            st.plotly_chart(
                gauge_chart(prob_real, "Real News Score", "#00ffaa"),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="glass-card" style="padding:1.2rem 1rem;">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Fake Probability</div>', unsafe_allow_html=True)
            st.plotly_chart(
                gauge_chart(prob_fake, "Fake News Score", "#ff3250"),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="glass-card" style="padding:1.2rem 1rem;">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Probability Split</div>', unsafe_allow_html=True)
            st.plotly_chart(
                prob_bar(prob_fake, prob_real),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown('<div class="section-label" style="margin-top:1rem">Text Fingerprint</div>', unsafe_allow_html=True)
            st.plotly_chart(
                radar_chart(stats),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Row 2: text stats ─────────────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📊 Article Statistics</div>', unsafe_allow_html=True)
        s1, s2, s3, s4, s5 = st.columns(5)
        tiles = [
            (s1, str(stats["words"]),          "Words"),
            (s2, str(stats["sentences"]),       "Sentences"),
            (s3, str(stats["unique_words"]),    "Unique Words"),
            (s4, str(stats["avg_word_len"]),    "Avg Word Len"),
            (s5, str(stats["chars"]),           "Characters"),
        ]
        for col, val, lbl in tiles:
            with col:
                st.markdown(f"""
                <div class="stat-tile">
                    <div class="stat-value">{val}</div>
                    <div class="stat-label">{lbl}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Model info ────────────────────────────────────────────────────────
        with st.expander("ℹ  Model Details & Interpretation"):
            st.markdown("""
**Model:** Logistic Regression with TF-IDF vectorization  
**Training data:** ~44,000 articles (Fake.csv + True.csv dataset)  
**Test-set accuracy:** ~98–99%  

**How to read the scores:**
- **Confidence ≥ 80%** → High certainty verdict  
- **Confidence 60–80%** → Moderate certainty; cross-check with other sources  
- **Confidence < 60%** → Low certainty; treat as inconclusive  

**Limitations:** The model is trained on a specific English-language dataset and may not generalise perfectly to satire, opinion pieces, or non-English content.
            """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">FakeShield · Built with Streamlit · Model: Logistic Regression + TF-IDF</div>',
            unsafe_allow_html=True)
