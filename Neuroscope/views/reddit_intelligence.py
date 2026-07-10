import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import re

from utils.reddit_fetcher import fetch_reddit_comments, fetch_reddit_post_metadata
from utils.inference import predict_text
from utils.charts import sentiment_chart, sarcasm_chart, emotion_chart
from components.reaction_cards import render_reaction_card
from components.insight_panels import render_community_insight
from services.analytics_service import (
    calculate_community_metrics,
    prepare_reaction_df,
    select_diverse_reactions,
)


# =====================================================
# HELPERS — render raw HTML without Streamlit escaping
# =====================================================

def html(content: str):
    """Render a raw HTML string. Strips leading whitespace so Streamlit
    never mistakes it for a fenced code block."""
    st.markdown(content.strip(), unsafe_allow_html=True)


def spacer(rem: float = 1.0):
    html(f'<div style="height:{rem}rem"></div>')


# =====================================================
# THEME
# =====================================================

def inject_theme():
    html("""<style>


:root {
    --bg-primary:    #FAFAFA;
    --bg-secondary:  #F4F4F5;
    --bg-card:       #ffffff;
    --bg-card-alt:   #f9f8f5;
    --border:        #d6d2c8;
    --border-strong: #b8b2a6;
    --text-primary:  #111827;
    --text-secondary:#374151;
    --text-muted:    #8a8780;
    --accent:        #1a4f8a;
    --accent-light:  #2563b0;
    --accent-bg:     #e8f0f9;
    --positive:      #1a6b3a;
    --negative:      #8b1f1f;
    --neutral:       #5a574f;
    --sarcasm:       #8b5e1a;
    --sarcasm-bg:    #fdf4e3;
    --radius:        4px;
    --radius-lg:     8px;
    --mono: monospace;
    --sans: sans-serif;
}

[data-theme="dark"], .dark {
    --bg-primary:    #0F172A;
    --bg-secondary:  #111214;
    --bg-card:       #111827;
    --bg-card-alt:   #232326;
    --border:        #2F2F35;
    --border-strong: #474750;
    --text-primary:  #FAFAFA;
    --text-secondary:#E5E7EB;
    --text-muted:    #A1A1AA;
    --accent:        #60A5FA;
    --accent-light:  #93C5FD;
    --accent-bg:     rgba(96,165,250,0.12);
    --positive:      #4ADE80;
    --negative:      #F87171;
    --neutral:       #D4D4D8;
    --sarcasm:       #C084FC;
    --sarcasm-bg:    rgba(192,132,252,0.12);
}



html, body, [class*="css"] { background-color: var(--bg-primary) !important; color: var(--text-primary) !important; font-size: 16px !important; }
.stApp { background-color: var(--bg-primary) !important; }
[data-testid="stHeader"] { display:none !important; }
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 1rem !important;
}

/* ---- Inputs ---- */
.stTextInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
    font-size: 1rem !important;
}

/* ---- Button ---- */
.stButton > button {
    background-color: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--mono) !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.6rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.82 !important; }

.stDownloadButton > button {
    background-color: var(--bg-card) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: var(--radius) !important;
    font-family: var(--mono) !important;
    font-size: 0.95rem !important;
}

/* ---- Metrics ---- */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    font-family: var(--mono) !important;
    font-size: 0.9rem !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    font-size: 2.4rem !important;
    font-weight: 600 !important;
}

/* ---- Progress bar ---- */
[data-testid="stProgressBar"] { height: 6px !important; border-radius: 3px !important; background: var(--border) !important; }
[data-testid="stProgressBar"] > div { background-color: var(--accent) !important; border-radius: 3px !important; height: 6px !important; }
.stProgress > div > div { background: var(--border) !important; border-radius: 3px !important; }
.stProgress > div > div > div { background: var(--accent) !important; border-radius: 3px !important; }
.stProgress > div > div > div > div { background: var(--accent) !important; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] { gap: 0 !important; border-bottom: 2px solid var(--border) !important; background: transparent !important; }
.stTabs [data-baseweb="tab"] { font-family: var(--mono) !important; font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; color: var(--text-muted) !important; padding: 0.5rem 1.2rem !important; background: transparent !important; border: none !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

/* ---- Expander ---- */
.streamlit-expanderHeader { font-family: var(--mono) !important; font-size: 0.95rem !important; background: var(--bg-card-alt) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }

/* ---- Misc ---- */
hr { border-color: var(--border) !important; }
.stCaption { font-size: 0.95rem !important; color: var(--text-secondary) !important; opacity: 0.95; }
.stCheckbox label { font-family: var(--mono) !important; font-size: 0.95rem !important; }
.stDataFrame { border: 1px solid var(--border) !important; border-radius: var(--radius-lg) !important; }
</style>""")


# =====================================================
# COMPONENTS
# =====================================================

def page_header():
    html('<div style="padding:2.5rem 0 1.5rem 0;border-bottom:2px solid var(--border-strong);margin-bottom:2rem;">'
         '<div style="font-family:var(--mono);font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--text-muted);margin-bottom:0.5rem;">Dual-Transformer NLP System · DeBERTa + RoBERTa</div>'
         '<h1 style="font-size:2.2rem;font-weight:700;letter-spacing:-0.03em;margin:0 0 0.6rem 0;color:var(--text-primary);font-family:var(--sans);">Reddit Community Intelligence</h1>'
         '<p style="font-family:var(--sans);font-size:0.95rem;color:var(--text-secondary);margin:0;font-weight:300;max-width:600px;line-height:1.6;">Live sentiment, sarcasm, and emotion analysis of Reddit discussions using fine-tuned transformer models. Multi-task inference with cross-model consensus scoring.</p>'
         '</div>')


def section_label(text, tag=None):
    tag_html = f'<span style="font-family:var(--mono);font-size:0.68rem;color:var(--accent);background:var(--accent-bg);padding:0.15rem 0.5rem;border-radius:2px;letter-spacing:0.05em;margin-left:0.7rem;">{tag}</span>' if tag else ""
    html(f'<div style="display:flex;align-items:center;margin:2rem 0 1rem 0;"><span style="font-family:var(--mono);font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--text-muted);white-space:nowrap;padding-right:0.8rem;">{text}</span>{tag_html}<div style="flex:1;height:1px;background:var(--border);"></div></div>')


def stat_card(label, value, sublabel=None, accent=False):
    color = "var(--accent)" if accent else "var(--text-primary)"
    sub = f'<div style="font-family:var(--mono);font-size:0.68rem;color:var(--text-muted);margin-top:0.15rem;">{sublabel}</div>' if sublabel else ""
    return (f'<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1rem 1.2rem;">'
            f'<div style="font-family:var(--mono);font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:0.3rem;">{label}</div>'
            f'<div style="font-family:var(--mono);font-size:1.8rem;font-weight:600;color:{color};line-height:1;">{value}</div>'
            f'{sub}</div>')


# =====================================================
# MODEL COMPARISON CARD
# =====================================================

def model_comparison_card(deberta_metrics, roberta_metrics, agreement_pct):
    def sentiment_color(s):
        s = s.lower()
        if "positive" in s: return "var(--positive)"
        if "negative" in s: return "var(--negative)"
        return "var(--neutral)"

    def bar_row(label_d, val_d, label_r, val_r, color):
        d = min(float(val_d), 100)
        r = min(float(val_r), 100)
        return (f'<div style="margin-bottom:1.2rem;">'
                f'<div style="font-family:var(--mono);font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.45rem;">{label_d}</div>'
                f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">'
                f'<span style="font-family:var(--mono);font-size:0.65rem;color:var(--text-muted);width:52px;">DeBERTa</span>'
                f'<div style="flex:1;height:5px;background:var(--border);border-radius:2px;"><div style="width:{d:.1f}%;height:100%;background:{color};border-radius:2px;"></div></div>'
                f'<span style="font-family:var(--mono);font-size:0.72rem;font-weight:600;color:{color};width:42px;text-align:right;">{d:.1f}%</span></div>'
                f'<div style="display:flex;align-items:center;gap:0.5rem;">'
                f'<span style="font-family:var(--mono);font-size:0.65rem;color:var(--text-muted);width:52px;">RoBERTa</span>'
                f'<div style="flex:1;height:5px;background:var(--border);border-radius:2px;"><div style="width:{r:.1f}%;height:100%;background:{color};opacity:0.65;border-radius:2px;"></div></div>'
                f'<span style="font-family:var(--mono);font-size:0.72rem;font-weight:600;color:{color};opacity:0.65;width:42px;text-align:right;">{r:.1f}%</span></div>'
                f'</div>')

    strength = "HIGH" if agreement_pct > 75 else ("MODERATE" if agreement_pct > 50 else "LOW")
    strength_color = "var(--positive)" if agreement_pct > 75 else ("var(--sarcasm)" if agreement_pct > 50 else "var(--negative)")

    bars = (bar_row("Positive Sentiment", deberta_metrics['positive_pct'], "roberta", roberta_metrics['positive_pct'], "var(--positive)") +
            bar_row("Negative Sentiment", deberta_metrics['negative_pct'], "roberta", roberta_metrics['negative_pct'], "var(--negative)") +
            bar_row("Sarcasm Rate", deberta_metrics['sarcasm_pct'], "roberta", roberta_metrics['sarcasm_pct'], "var(--sarcasm)"))

    dc = sentiment_color(deberta_metrics['dominant_sentiment'])
    rc = sentiment_color(roberta_metrics['dominant_sentiment'])

    html(f'<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.6rem;margin-bottom:1rem;">'
         f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.6rem;flex-wrap:wrap;gap:1rem;">'
         f'<div><div style="font-family:var(--mono);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);margin-bottom:0.3rem;">Cross-Model Consensus</div>'
         f'<div style="font-family:var(--mono);font-size:2.4rem;font-weight:700;color:var(--text-primary);line-height:1;">{agreement_pct:.1f}%</div></div>'
         f'<div style="background:var(--accent-bg);border:1px solid var(--accent);border-radius:var(--radius);padding:0.4rem 0.8rem;font-family:var(--mono);font-size:0.7rem;font-weight:600;color:{strength_color};letter-spacing:0.1em;">CONSENSUS · {strength}</div>'
         f'</div>'
         f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;">{bars}<div></div></div>'
         f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;padding-top:1.2rem;border-top:1px solid var(--border);margin-top:0.4rem;">'
         f'<div><div style="font-family:var(--mono);font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.3rem;">DeBERTa Dominant</div>'
         f'<div style="font-family:var(--mono);font-size:0.82rem;font-weight:600;color:{dc};">{deberta_metrics["dominant_sentiment"]}</div>'
         f'<div style="font-family:var(--sans);font-size:0.78rem;color:var(--text-secondary);margin-top:0.15rem;">{deberta_metrics["dominant_emotion"]}</div></div>'
         f'<div><div style="font-family:var(--mono);font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.3rem;">RoBERTa Dominant</div>'
         f'<div style="font-family:var(--mono);font-size:0.82rem;font-weight:600;color:{rc};">{roberta_metrics["dominant_sentiment"]}</div>'
         f'<div style="font-family:var(--sans);font-size:0.78rem;color:var(--text-secondary);margin-top:0.15rem;">{roberta_metrics["dominant_emotion"]}</div></div>'
         f'</div></div>')


# =====================================================
# ADVANCED: EMOTION TIMELINE
# =====================================================

def render_emotion_timeline(deberta_df, roberta_df):
    section_label("Emotion Timeline", "Advanced")
    st.caption("Emotional trajectory across the comment thread — rolling window smoothing")

    emotion_colors = {
        "joy": "#3aaa65", "anger": "#e05555", "sadness": "#4a90d9",
        "fear": "#9b59b6", "surprise": "#f39c12", "disgust": "#e67e22",
        "trust": "#27ae60", "anticipation": "#2980b9",
        "neutral": "#8a8780", "love": "#e91e8c",
    }

    window = max(1, len(deberta_df) // 20)
    emotions = deberta_df["emotion"].tolist()
    unique_emotions = list(set(emotions))

    rows = []
    for i in range(len(emotions)):
        chunk = emotions[max(0, i - window): i + window + 1]
        c = Counter(chunk)
        total = len(chunk)
        row = {"index": i}
        for e in unique_emotions:
            row[e] = c.get(e, 0) / total * 100
        rows.append(row)
    smooth_df = pd.DataFrame(rows)

    fig = go.Figure()
    for emotion in unique_emotions:
        color = emotion_colors.get(emotion.lower(), "#8a8780")
        fig.add_trace(go.Scatter(
            x=smooth_df["index"], y=smooth_df[emotion],
            name=emotion.title(), mode="lines",
            line=dict(width=2, color=color),
            hovertemplate=f"<b>{emotion}</b>: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
        xaxis=dict(title="Comment Index", gridcolor="rgba(120,120,120,0.12)", showgrid=True, zeroline=False),
        yaxis=dict(title="Prevalence (%)", gridcolor="rgba(120,120,120,0.12)", showgrid=True, zeroline=False),
        margin=dict(l=0, r=0, t=36, b=0), height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# ADVANCED: SARCASM HEATMAP
# =====================================================

def render_sarcasm_heatmap(deberta_df, roberta_df):
    section_label("Sarcasm Density Heatmap", "Advanced")
    st.caption("Sarcasm confidence per comment — each cell = one comment, brighter = more confident")

    n = min(len(deberta_df), len(roberta_df), 100)
    d_conf = deberta_df["sarcasm_conf"].values[:n]
    r_conf = roberta_df["sarcasm_conf"].values[:n]

    cols = 10
    rows_n = int(np.ceil(n / cols))
    d_grid = np.full((rows_n, cols), np.nan)
    r_grid = np.full((rows_n, cols), np.nan)

    for i in range(n):
        ri, ci = divmod(i, cols)
        d_grid[ri][ci] = d_conf[i]
        r_grid[ri][ci] = r_conf[i]

    col1, col2 = st.columns(2)

    def make_heatmap(grid, title, colorscale):
        fig = go.Figure(go.Heatmap(
            z=grid, colorscale=colorscale, zmin=0, zmax=1,
            showscale=True,
            colorbar=dict(thickness=10, tickfont=dict(family="IBM Plex Mono", size=9), tickformat=".0%"),
            hovertemplate="Row %{y}, Col %{x}<br>Confidence: %{z:.2f}<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(family="IBM Plex Mono", size=11), x=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            margin=dict(l=0, r=0, t=36, b=0), height=220,
        )
        return fig

    with col1:
        st.plotly_chart(make_heatmap(d_grid, "DeBERTa · Sarcasm Confidence",
            [[0,"#1c1e21"],[0.4,"#3d2a00"],[0.7,"#8b5e1a"],[1.0,"#f5c518"]]), use_container_width=True)
    with col2:
        st.plotly_chart(make_heatmap(r_grid, "RoBERTa · Sarcasm Confidence",
            [[0,"#1c1e21"],[0.4,"#0a1929"],[0.7,"#1a4f8a"],[1.0,"#6aabf7"]]), use_container_width=True)


# =====================================================
# ADVANCED: KEYWORD EXTRACTION
# =====================================================

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","it","this","that","was","are","be","as","by","from","have","had",
    "has","not","they","he","she","we","you","i","my","your","his","her",
    "our","their","its","so","if","do","did","does","will","would","could",
    "should","can","just","like","get","got","no","yes","what","how","when",
    "who","which","all","also","more","some","there","been","were","than",
    "then","up","out","about","into","other","me","him","us","even","re",
    "ve","ll","s","t","don","doesn","didn","isn","wasn","weren","haven",
    "https","www","reddit","http","com","amp","gt","lt","one","two","three",
}

def render_word_cloud(comments):
    section_label("Keyword Extraction", "Advanced")
    st.caption("Most frequent meaningful terms — size and opacity reflect frequency")

    text = " ".join(comments).lower()
    tokens = [t for t in re.findall(r'\b[a-z]{3,}\b', text) if t not in STOPWORDS]
    counts = Counter(tokens).most_common(50)

    if not counts:
        st.info("No keywords extracted.")
        return

    words, freqs = zip(*counts)
    max_f, min_f = freqs[0], freqs[-1]

    def scale(f): return 0.72 + 1.4 * (f - min_f) / (max_f - min_f + 1e-9)
    def alpha(f): return 0.38 + 0.62 * (f - min_f) / (max_f - min_f + 1e-9)

    items = "".join(
        f'<span style="font-family:var(--mono);font-size:{scale(f):.2f}rem;font-weight:{"600" if scale(f)>1.4 else "400"};color:var(--accent);opacity:{alpha(f):.2f};padding:0.2rem 0.35rem;display:inline-block;" title="{f} occurrences">{w}</span>'
        for w, f in counts
    )
    html(f'<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.5rem;line-height:2.2;text-align:center;">{items}</div>')

    with st.expander("Frequency table"):
        kw_df = pd.DataFrame(counts, columns=["Term", "Count"])
        kw_df["% of top"] = (kw_df["Count"] / kw_df["Count"].max() * 100).round(1)
        st.dataframe(kw_df, use_container_width=True, hide_index=True)


# =====================================================
# ADVANCED: COMMENT DRILL-DOWN
# =====================================================

def render_comment_drilldown(deberta_df, roberta_df):
    section_label("Comment Drill-Down", "Advanced")
    st.caption("Search and inspect per-comment predictions from both models")

    n = min(len(deberta_df), len(roberta_df))
    col_s, col_f = st.columns([2, 1])
    with col_s:
        search_query = st.text_input("Filter by keyword", placeholder="Search comments…", key="dd_search", label_visibility="collapsed")
    with col_f:
        filter_sent = st.selectbox("Sentiment filter", ["All", "Positive", "Negative", "Neutral"], key="dd_sent", label_visibility="collapsed")

    def s_color(s):
        s = s.lower()
        if "positive" in s: return "var(--positive)"
        if "negative" in s: return "var(--negative)"
        return "var(--neutral)"

    def sarcasm_badge(s, conf):
        is_s = "sarcastic" in str(s).lower()
        col = "var(--sarcasm)" if is_s else "var(--border-strong)"
        label = "SARCASTIC" if is_s else "sincere"
        return f'<span style="font-family:var(--mono);font-size:0.62rem;color:{col};border:1px solid {col};padding:0.1rem 0.4rem;border-radius:2px;">{label} {conf*100:.0f}%</span>'

    shown = 0
    for i in range(n):
        d = deberta_df.iloc[i]
        r = roberta_df.iloc[i]
        text = str(d.get("comment", ""))

        if search_query and search_query.lower() not in text.lower():
            continue
        if filter_sent != "All" and filter_sent.lower() not in str(d["sentiment"]).lower():
            continue

        shown += 1
        if shown > 50:
            st.caption("Showing first 50 filtered results.")
            break

        agree = d["sentiment"] == r["sentiment"]
        agree_color = "var(--positive)" if agree else "var(--sarcasm)"
        agree_text = "✓ Models agree on sentiment" if agree else "⚠ Models disagree on sentiment"
        preview = text[:150] + ("…" if len(text) > 150 else "")

        with st.expander(f"#{i+1} · {preview}"):
            c1, c2 = st.columns(2)
            with c1:
                html(f'<div style="font-family:var(--mono);font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.5rem;">DeBERTa</div>'
                     f'<div style="margin-bottom:0.35rem;"><span style="font-family:var(--mono);font-size:0.78rem;font-weight:600;color:{s_color(d["sentiment"])};">{d["sentiment"]}</span> <span style="font-family:var(--mono);font-size:0.65rem;color:var(--text-muted);">{d["sentiment_conf"]*100:.1f}%</span></div>'
                     f'<div style="margin-bottom:0.35rem;">{sarcasm_badge(d["sarcasm"], d["sarcasm_conf"])}</div>'
                     f'<div style="font-family:var(--sans);font-size:0.78rem;color:var(--text-secondary);">{d["emotion"]} <span style="color:var(--text-muted);">({d["emotion_conf"]*100:.1f}%)</span></div>')
            with c2:
                html(f'<div style="font-family:var(--mono);font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.5rem;">RoBERTa</div>'
                     f'<div style="margin-bottom:0.35rem;"><span style="font-family:var(--mono);font-size:0.78rem;font-weight:600;color:{s_color(r["sentiment"])};">{r["sentiment"]}</span> <span style="font-family:var(--mono);font-size:0.65rem;color:var(--text-muted);">{r["sentiment_conf"]*100:.1f}%</span></div>'
                     f'<div style="margin-bottom:0.35rem;">{sarcasm_badge(r["sarcasm"], r["sarcasm_conf"])}</div>'
                     f'<div style="font-family:var(--sans);font-size:0.78rem;color:var(--text-secondary);">{r["emotion"]} <span style="color:var(--text-muted);">({r["emotion_conf"]*100:.1f}%)</span></div>')
            html(f'<div style="margin-top:0.7rem;padding:0.4rem 0.7rem;background:var(--bg-card-alt);border-left:2px solid {agree_color};font-family:var(--mono);font-size:0.68rem;color:var(--text-muted);">{agree_text}</div>'
                 f'<div style="margin-top:0.6rem;font-family:var(--sans);font-size:0.82rem;color:var(--text-secondary);line-height:1.6;padding:0.7rem;background:var(--bg-card-alt);border-radius:var(--radius);border:1px solid var(--border);">{text}</div>')

    if shown == 0:
        st.info("No comments match the current filters.")


# =====================================================
# SHARED TAB RENDERER — identical charts for both models
# =====================================================

_EMOTION_STYLES = {
    "joy":          {"accent": "#FACC15", "g1": "#3B2F0E", "g2": "#1E1B0F"},
    "amusement":    {"accent": "#818CF8", "g1": "#1E1B4B", "g2": "#172554"},
    "anger":        {"accent": "#F87171", "g1": "#3F0D0D", "g2": "#1F1111"},
    "sadness":      {"accent": "#60A5FA", "g1": "#172554", "g2": "#0F172A"},
    "fear":         {"accent": "#C084FC", "g1": "#2E1065", "g2": "#1E1B4B"},
    "surprise":     {"accent": "#FB923C", "g1": "#431407", "g2": "#1C1917"},
    "disgust":      {"accent": "#A3E635", "g1": "#1a2e05", "g2": "#0f172a"},
    "trust":        {"accent": "#34D399", "g1": "#064e3b", "g2": "#0f172a"},
    "anticipation": {"accent": "#F472B6", "g1": "#500724", "g2": "#0f172a"},
    "neutral":      {"accent": "#94A3B8", "g1": "#1E293B", "g2": "#0F172A"},
}


def _sentiment_flow_chart(df, prefix):
    vals = [1 if s == "positive" else -1 if s == "negative" else 0 for s in df["sentiment"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(vals))), y=vals,
        mode="lines", name="Sentiment Flow",
        line=dict(width=1.5, color="var(--accent, #4a90d9)"),
        fill="tozeroy", fillcolor="rgba(74,144,217,0.08)",
        hovertemplate="Comment %{x}<br>Sentiment: %{y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", size=10),
        xaxis=dict(title="Comment Index", gridcolor="rgba(120,120,120,0.12)", zeroline=False),
        yaxis=dict(title="Sentiment", tickvals=[-1, 0, 1], ticktext=["Negative", "Neutral", "Positive"],
                   gridcolor="rgba(120,120,120,0.12)", zeroline=True, zerolinecolor="rgba(120,120,120,0.25)"),
        hovermode="x unified", height=280, margin=dict(l=0, r=0, t=8, b=0),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"{prefix}_flow")


def _emotion_heatmap_chart(df, prefix):
    matrix = pd.crosstab(df["emotion"], df["sentiment"])
    fig = px.imshow(
        matrix, text_auto=True, aspect="auto",
        color_continuous_scale=[[0, "#0e0f11"], [0.5, "#1a4f8a"], [1.0, "#6aabf7"]],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", size=10),
        coloraxis_colorbar=dict(thickness=10, tickfont=dict(family="IBM Plex Mono", size=9)),
        margin=dict(l=0, r=0, t=8, b=0), height=320,
        xaxis=dict(title="Sentiment"), yaxis=dict(title="Emotion"),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"{prefix}_heatmap")


def _high_sarcasm_cards(df, prefix):
    sarcastic = df[df["sarcasm"].str.lower().str.contains("sarcastic", na=False)].head(5)
    if sarcastic.empty:
        st.info("No sarcastic comments detected.")
        return
    for i, (_, row) in enumerate(sarcastic.iterrows()):
        emotion = str(row.get("emotion", "neutral")).lower()
        style = _EMOTION_STYLES.get(emotion, _EMOTION_STYLES["neutral"])
        sentiment = str(row.get("sentiment", "neutral"))
        sarcasm_conf = float(row.get("sarcasm_conf", 0)) * 100
        s_color = "var(--positive)" if "positive" in sentiment.lower() else ("var(--negative)" if "negative" in sentiment.lower() else "var(--neutral)")
        comment_text = str(row.get("comment", ""))
        html(
            f'<div style="background:linear-gradient(135deg,{style["g1"]},{style["g2"]});border:1px solid rgba(255,255,255,0.06);border-radius:var(--radius-lg);padding:1.2rem;margin-bottom:0.8rem;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.7rem;">'
            f'<div style="display:flex;align-items:center;gap:0.6rem;">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{style["accent"]};box-shadow:0 0 10px {style["accent"]};"></div>'
            f'<span style="font-family:var(--mono);font-size:0.82rem;font-weight:600;color:#f8fafc;">{emotion.title()}</span>'
            f'</div>'
            f'<div style="display:flex;gap:0.5rem;align-items:center;">'
            f'<span style="font-family:var(--mono);font-size:0.65rem;font-weight:600;color:{s_color};border:1px solid {s_color};padding:0.1rem 0.5rem;border-radius:2px;">{sentiment.upper()}</span>'
            f'<span style="font-family:var(--mono);font-size:0.65rem;font-weight:600;color:var(--sarcasm);border:1px solid var(--sarcasm);padding:0.1rem 0.5rem;border-radius:2px;">SARCASTIC {sarcasm_conf:.0f}%</span>'
            f'</div></div>'
            f'<div style="font-family:var(--sans);font-size:0.95rem;color:#F8FAFC;line-height:1.8;padding:0.6rem 0.7rem;background:rgba(0,0,0,0.2);border-radius:var(--radius);">{comment_text}</div>'
            f'</div>'
        )


def _render_model_tab(df, metrics, prefix):
    # 1. Insight panel
    render_community_insight(
        metrics["positive_pct"], metrics["negative_pct"],
        metrics["sarcasm_pct"], metrics["dominant_sentiment"],
        metrics["dominant_emotion"],
    )
    # 2. Sentiment + Sarcasm side by side
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(sentiment_chart(df), use_container_width=True, key=f"{prefix}_sentiment")
    with c2:
        st.plotly_chart(sarcasm_chart(df), use_container_width=True, key=f"{prefix}_sarcasm")
    # 3. Emotion distribution
    st.plotly_chart(emotion_chart(df), use_container_width=True, key=f"{prefix}_emotion")
    # 4. Sentiment flow timeline
    html('<div style="font-family:var(--mono);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);margin:1.2rem 0 0.5rem 0;">Community Sentiment Flow</div>')
    st.caption("Sentiment polarity across the thread in comment order")
    _sentiment_flow_chart(df, prefix)
    # 5. Emotion × Sentiment heatmap
    html('<div style="font-family:var(--mono);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);margin:1.2rem 0 0.5rem 0;">Emotion × Sentiment Distribution</div>')
    st.caption("Cross-tabulation of emotion labels against sentiment classes")
    _emotion_heatmap_chart(df, prefix)
    # 6. High sarcasm reaction cards
    html('<div style="font-family:var(--mono);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);margin:1.2rem 0 0.5rem 0;">High Sarcasm Reactions</div>')
    st.caption("Top sarcastic comments with emotion and sentiment context")
    _high_sarcasm_cards(df, prefix)


# =====================================================
# CROSS-MODEL CHARTS (outside tabs)
# =====================================================

def _render_emotion_radar(deberta_df, roberta_df):
    d_counts = deberta_df["emotion"].value_counts()
    r_counts = roberta_df["emotion"].value_counts()
    all_emotions = sorted(set(d_counts.index) | set(r_counts.index))
    d_vals = [int(d_counts.get(e, 0)) for e in all_emotions]
    r_vals = [int(r_counts.get(e, 0)) for e in all_emotions]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=d_vals, theta=all_emotions, fill="toself", name="DeBERTa",
                                  line=dict(color="#4a90d9", width=2), fillcolor="rgba(74,144,217,0.12)"))
    fig.add_trace(go.Scatterpolar(r=r_vals, theta=all_emotions, fill="toself", name="RoBERTa",
                                  line=dict(color="#d4a03a", width=2), fillcolor="rgba(212,160,58,0.10)"))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="rgba(120,120,120,0.2)", tickfont=dict(family="IBM Plex Mono", size=9)),
            angularaxis=dict(gridcolor="rgba(120,120,120,0.2)", tickfont=dict(family="IBM Plex Mono", size=9)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=10)),
        showlegend=True, height=480, margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True, key="emotion_radar")


def _render_agreement_bar(deberta_df, roberta_df, n_cmp):
    labels, d_sentiments, r_sentiments, agreements = [], [], [], []
    for i in range(n_cmp):
        d_s = deberta_df.iloc[i]["sentiment"]
        r_s = roberta_df.iloc[i]["sentiment"]
        labels.append(f"#{i+1}")
        d_sentiments.append(d_s)
        r_sentiments.append(r_s)
        agreements.append("Agree" if d_s == r_s else "Disagree")

    counts = Counter(agreements)
    fig = go.Figure()
    colors = {"Agree": "#3aaa65", "Disagree": "#e05555"}
    for label, count in counts.items():
        fig.add_trace(go.Bar(
            x=[label], y=[count], name=label,
            marker_color=colors.get(label, "#8a8780"),
            text=[count], textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11),
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", size=10),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Comment Count", gridcolor="rgba(120,120,120,0.12)"),
        showlegend=False, height=260, margin=dict(l=0, r=0, t=20, b=0), bargap=0.5,
    )
    st.plotly_chart(fig, use_container_width=True, key="agreement_bar")


def _render_full_comparison_table(deberta_df, roberta_df):
    rows = []
    for category, col in [("Sentiment", "sentiment"), ("Emotion", "emotion"), ("Sarcasm", "sarcasm")]:
        all_labels = sorted(set(deberta_df[col]) | set(roberta_df[col]))
        for label in all_labels:
            d_pct = (deberta_df[col] == label).mean() * 100
            r_pct = (roberta_df[col] == label).mean() * 100
            delta = d_pct - r_pct
            rows.append({
                "Category": category,
                "Class": label,
                "DeBERTa %": f"{d_pct:.1f}%",
                "RoBERTa %": f"{r_pct:.1f}%",
                "Delta": f"{delta:+.1f}pp",
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# =====================================================
# MAIN
# =====================================================

def render():
    inject_theme()
    page_header()

    # --- INPUTS ---
    section_label("Configuration")
    col_url, col_slider = st.columns([3, 2])
    with col_url:
        reddit_url = st.text_input("URL", placeholder="https://www.reddit.com/r/…", label_visibility="collapsed")
    with col_slider:
        comment_limit = st.slider("Comments", min_value=10, max_value=500, value=100, step=10)
    include_replies = st.checkbox("Include nested replies")
    analyze_clicked = st.button("Run Analysis →")

    if not analyze_clicked:
        return
    if not reddit_url.strip():
        st.warning("Enter a Reddit URL to proceed.")
        return

    # --- FETCH ---
    with st.spinner("Fetching Reddit discussion…"):
        try:
            metadata = fetch_reddit_post_metadata(reddit_url)
            comments = fetch_reddit_comments(reddit_url, limit=comment_limit, include_replies=include_replies)
        except Exception as e:
            st.error(f"Failed to fetch Reddit discussion: {e}")
            return

    if not comments:
        st.error("No comments extracted. Check the URL, or the thread may be private/deleted.")
        return

    # --- DISCUSSION OVERVIEW ---
    section_label("Discussion Overview")
    cols = st.columns(4)
    for col, (label, value) in zip(cols, [
        ("Subreddit",      metadata.get("subreddit", "—")),
        ("Upvotes",        f"{metadata.get('score', 0):,}"),
        ("Total Comments", f"{metadata.get('num_comments', 0):,}"),
        ("Analyzed",       str(len(comments))),
    ]):
        with col:
            html(stat_card(label, value))

    spacer(0.8)
    html(f'<div style="font-family:var(--sans);font-size:1.05rem;font-weight:600;color:var(--text-primary);padding:0.7rem 0;border-bottom:1px solid var(--border);">{metadata.get("title", "Unknown Discussion")}</div>')

    # --- INFERENCE ---
    section_label("Transformer Inference")
    deberta_results, roberta_results = [], []
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    total_steps = len(comments) * 2
    current_step = 0

    for idx, comment in enumerate(comments):
        status_placeholder.markdown(
            f'<p style="font-family:var(--mono);font-size:0.75rem;color:var(--text-muted);margin:0.3rem 0;">Processing {idx + 1} / {len(comments)}</p>',
            unsafe_allow_html=True,
        )
        for model_key, results in [("DeBERTa", deberta_results), ("RoBERTa", roberta_results)]:
            try:
                pred = predict_text(comment, model_key)
                pred["comment"] = comment
                results.append(pred)
            except Exception as e:
                status_placeholder.empty()
                progress_bar.empty()
                st.error(f"Transformer inference failed on comment {idx + 1} with {model_key}: {e}")
                return
            current_step += 1
            progress_bar.progress(current_step / total_steps)

    status_placeholder.empty()
    progress_bar.empty()

    if not deberta_results or not roberta_results:
        st.error("Transformer inference failed. Check model checkpoints.")
        return

    deberta_df = pd.DataFrame(deberta_results)
    roberta_df = pd.DataFrame(roberta_results)

    # --- METRICS & CONSENSUS ---
    deberta_metrics = calculate_community_metrics(deberta_df)
    roberta_metrics = calculate_community_metrics(roberta_df)
    n_cmp = min(len(deberta_df), len(roberta_df))
    agreement_count = int((deberta_df["sentiment"].values[:n_cmp] == roberta_df["sentiment"].values[:n_cmp]).sum())
    agreement_pct = agreement_count / n_cmp * 100

    # --- CONSENSUS CARD ---
    section_label("Cross-Model Analysis")
    model_comparison_card(deberta_metrics, roberta_metrics, agreement_pct)

    # --- MODEL ANALYTICS TABS ---
    section_label("Model Analytics")
    tab_d, tab_r = st.tabs(["DeBERTa", "RoBERTa"])

    with tab_d:
        _render_model_tab(deberta_df, deberta_metrics, prefix="d")
    with tab_r:
        _render_model_tab(roberta_df, roberta_metrics, prefix="r")

    # --- ADVANCED FEATURES ---
    render_emotion_timeline(deberta_df, roberta_df)
    render_sarcasm_heatmap(deberta_df, roberta_df)
    render_word_cloud(comments)

    # --- EMOTION RADAR ---
    section_label("Emotion Intelligence Comparison", "Advanced")
    st.caption("Emotion distribution overlap — DeBERTa vs RoBERTa")
    _render_emotion_radar(deberta_df, roberta_df)

    # --- AGREEMENT ANALYTICS ---
    section_label("Agreement Analytics")
    _render_agreement_bar(deberta_df, roberta_df, n_cmp)

    # --- DRILL-DOWN ---
    render_comment_drilldown(deberta_df, roberta_df)

    # --- FULL COMPARISON TABLE ---
    section_label("Full Class-Level Comparison")
    _render_full_comparison_table(deberta_df, roberta_df)

    # --- EXPORT ---
    section_label("Export")
    e1, e2 = st.columns(2)
    with e1:
        st.download_button("↓ DeBERTa CSV", deberta_df.to_csv(index=False).encode(), "deberta_analysis.csv", "text/csv")
    with e2:
        st.download_button("↓ RoBERTa CSV", roberta_df.to_csv(index=False).encode(), "roberta_analysis.csv", "text/csv")

    spacer(2)