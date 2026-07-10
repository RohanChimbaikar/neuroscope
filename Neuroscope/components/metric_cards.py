import streamlit as st
import streamlit.components.v1 as components


_METRIC_CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: 'Inter', sans-serif;
}

/* LIGHT MODE */

:root {

    --sentiment-bg:
        linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);

    --sarcasm-bg:
        linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);

    --emotion-bg:
        linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);

    --sentiment-border: rgba(37,99,235,0.18);
    --sarcasm-border: rgba(245,158,11,0.18);
    --emotion-border: rgba(139,92,246,0.18);

    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;

    --shadow:
        0 4px 14px rgba(15,23,42,0.06),
        0 12px 30px rgba(15,23,42,0.08);

    --shadow-hover:
        0 10px 24px rgba(15,23,42,0.10),
        0 24px 48px rgba(15,23,42,0.12);
}

@media (prefers-color-scheme: dark) {

    :root {

        --sentiment-bg:
            linear-gradient(135deg, #172554 0%, #1e3a8a 100%);

        --sarcasm-bg:
            linear-gradient(135deg, #451a03 0%, #78350f 100%);

        --emotion-bg:
            linear-gradient(135deg, #2e1065 0%, #4c1d95 100%);

        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;

        --shadow:
            0 8px 24px rgba(0,0,0,0.32);

        --shadow-hover:
            0 12px 36px rgba(0,0,0,0.42);
    }
}

.ns-wrapper {

    width: 100%;
    padding: 12px 6px 24px 6px;
}

.ns-metric-row {

    display: grid;
    grid-template-columns: repeat(3, minmax(0,1fr));

    gap: 22px;
}

/* CARD */

.ns-card {

    position: relative;

    overflow: hidden;

    border-radius: 28px;

    padding: 26px;

    transition:
        transform 0.22s ease,
        box-shadow 0.22s ease;

    box-shadow: var(--shadow);
}

.ns-card:hover {

    transform: translateY(-4px);

    box-shadow: var(--shadow-hover);
}

/* CARD THEMES */

.ns-card.sentiment {

    background: var(--sentiment-bg);
    border: 1px solid var(--sentiment-border);
}

.ns-card.sarcasm {

    background: var(--sarcasm-bg);
    border: 1px solid var(--sarcasm-border);
}

.ns-card.emotion {

    background: var(--emotion-bg);
    border: 1px solid var(--emotion-border);
}

/* GLOW */

.ns-card::before {

    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    right: -60px;
    top: -60px;

    border-radius: 50%;

    opacity: 0.15;
}

.ns-card.sentiment::before {
    background: #3b82f6;
}

.ns-card.sarcasm::before {
    background: #f59e0b;
}

.ns-card.emotion::before {
    background: #8b5cf6;
}

/* TOP */

.ns-top {

    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 34px;

    position: relative;
    z-index: 2;
}

.ns-label {

    font-size: 13px;
    font-weight: 800;

    text-transform: uppercase;
    letter-spacing: 0.12em;

    color: var(--text-muted);
}

/* ICON */

.ns-icon {

    width: 52px;
    height: 52px;

    border-radius: 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 22px;
    font-weight: 700;

    background: rgba(255,255,255,0.22);

    backdrop-filter: blur(12px);

    color: white;
}

/* VALUE */

.ns-value {

    position: relative;
    z-index: 2;

    font-size: 54px;
    font-weight: 800;

    line-height: 1;
    letter-spacing: -0.06em;

    color: var(--text-primary);

    margin-bottom: 42px;

    text-transform: capitalize;
}

/* BOTTOM */

.ns-bottom {

    position: relative;
    z-index: 2;

    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 16px;
}

.ns-conf-label {

    font-size: 14px;
    font-weight: 600;

    color: var(--text-secondary);
}

.ns-conf-value {

    font-size: 18px;
    font-weight: 800;

    color: var(--text-primary);
}

/* BAR */

.ns-track {

    position: relative;
    z-index: 2;

    width: 100%;
    height: 12px;

    border-radius: 999px;

    overflow: hidden;

    background: rgba(255,255,255,0.28);
}

.ns-fill {

    height: 100%;
    border-radius: 999px;
}

/* BAR COLORS */

.ns-card.sentiment .ns-fill {

    background: linear-gradient(
        90deg,
        #3b82f6,
        #2563eb
    );
}

.ns-card.sarcasm .ns-fill {

    background: linear-gradient(
        90deg,
        #f59e0b,
        #ea580c
    );
}

.ns-card.emotion .ns-fill {

    background: linear-gradient(
        90deg,
        #a855f7,
        #7c3aed
    );
}

/* MOBILE */

@media (max-width: 900px) {

    .ns-metric-row {

        grid-template-columns: 1fr;
    }

    .ns-value {

        font-size: 42px;
    }
}

</style>
"""


def _card(kind, label, value, conf, icon):

    pct = round(conf * 100, 1)
    width = min(int(conf * 100), 100)

    return f"""
    <div class="ns-card {kind}">

        <div class="ns-top">

            <div class="ns-label">
                {label}
            </div>

            <div class="ns-icon">
                {icon}
            </div>

        </div>

        <div class="ns-value">
            {value}
        </div>

        <div class="ns-bottom">

            <div class="ns-conf-label">
                Confidence
            </div>

            <div class="ns-conf-value">
                {pct}%
            </div>

        </div>

        <div class="ns-track">

            <div
                class="ns-fill"
                style="width:{width}%"
            ></div>

        </div>

    </div>
    """


def render_single_prediction_metrics(result: dict):

    sentiment = result.get("sentiment", "neutral")
    sarcasm = result.get("sarcasm", "not sarcastic")
    emotion = result.get("emotion", "neutral")

    sentiment_icon = (
        "↗"
        if sentiment.lower() == "positive"
        else "↘"
        if sentiment.lower() == "negative"
        else "•"
    )

    sarcasm_icon = (
        "◎"
        if sarcasm.lower() == "sarcastic"
        else "✓"
    )

    emotion_icon = "◈"

    html = f"""
    <div class="ns-wrapper">

        <div class="ns-metric-row">

            {_card(
                "sentiment",
                "Sentiment",
                sentiment,
                result.get("sentiment_conf", 0),
                sentiment_icon
            )}

            {_card(
                "sarcasm",
                "Sarcasm",
                sarcasm,
                result.get("sarcasm_conf", 0),
                sarcasm_icon
            )}

            {_card(
                "emotion",
                "Emotion",
                emotion,
                result.get("emotion_conf", 0),
                emotion_icon
            )}

        </div>

    </div>
    """

    components.html(
        f"""
        {_METRIC_CSS}
        {html}
        """,
        height=340,
        scrolling=False
    )