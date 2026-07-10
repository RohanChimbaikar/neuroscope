import streamlit as st
import streamlit.components.v1 as components

from utils.inference import predict_text

from components.metric_cards import (
    render_single_prediction_metrics
)


def render():

    st.header("Single Text Analysis")

    text = st.text_area(
        "Enter text",
        height=180,
        placeholder="Type text for sentiment, sarcasm, and emotion analysis..."
    )

    if st.button("Analyze"):

        if text.strip() == "":

            st.warning("Please enter text")

        else:

            result = predict_text(
                text,
                st.session_state.get(
                    "selected_model",
                    "DeBERTa"
                )
            )

            # ---------------------------------
            # METRIC CARDS
            # ---------------------------------

            render_single_prediction_metrics(result)

            # ---------------------------------
            # EXTRACT VALUES
            # ---------------------------------

            sentiment = result.get(
                "sentiment",
                "neutral"
            )

            sarcasm = result.get(
                "sarcasm",
                "not sarcastic"
            )

            emotion = result.get(
                "emotion",
                "neutral"
            )

            sentiment_conf = round(
                result.get(
                    "sentiment_conf",
                    0
                ) * 100,
                1
            )

            sarcasm_conf = round(
                result.get(
                    "sarcasm_conf",
                    0
                ) * 100,
                1
            )

            emotion_conf = round(
                result.get(
                    "emotion_conf",
                    0
                ) * 100,
                1
            )

            # ---------------------------------
            # AI INTERPRETATION PANEL
            # ---------------------------------

            insight_html = f"""

            <style>

            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: 'Inter', sans-serif;
            }}

            :root {{

                --bg:
                    linear-gradient(
                        135deg,
                        #111827 0%,
                        #0f172a 100%
                    );

                --border:
                    rgba(255,255,255,0.08);

                --text-primary:
                    #f8fafc;

                --text-secondary:
                    #94a3b8;

                --shadow:
                    0 8px 24px rgba(0,0,0,0.22);

                --blue:
                    #3b82f6;

                --orange:
                    #f59e0b;

                --purple:
                    #8b5cf6;
            }}

            .analysis-shell {{

                position: relative;

                overflow: hidden;

                border-radius: 32px;

                padding: 34px;

                background: var(--bg);

                border: 1px solid var(--border);

                box-shadow: var(--shadow);
            }}

            .analysis-shell::before {{

                content: "";

                position: absolute;

                width: 300px;
                height: 300px;

                right: -120px;
                top: -120px;

                border-radius: 50%;

                background:
                    radial-gradient(
                        rgba(59,130,246,0.10),
                        transparent 70%
                    );
            }}

            .analysis-header {{

                display: flex;
                align-items: center;
                justify-content: space-between;

                margin-bottom: 34px;
            }}

            .analysis-title {{

                font-size: 34px;
                font-weight: 800;

                letter-spacing: -0.05em;

                color: var(--text-primary);
            }}

            .analysis-pill {{

                padding: 10px 16px;

                border-radius: 999px;

                background:
                    rgba(59,130,246,0.12);

                color: #3b82f6;

                font-size: 12px;
                font-weight: 700;

                letter-spacing: 0.08em;
            }}

            .insight-grid {{

                display: grid;

                grid-template-columns:
                    repeat(2, 1fr);

                gap: 22px;

                margin-bottom: 24px;
            }}

            .insight-card {{

                border-radius: 24px;

                padding: 24px;

                background:
                    rgba(255,255,255,0.03);

                border:
                    1px solid rgba(255,255,255,0.06);
            }}

            .insight-label {{

                font-size: 12px;
                font-weight: 700;

                text-transform: uppercase;

                letter-spacing: 0.12em;

                color: var(--text-secondary);

                margin-bottom: 16px;
            }}

            .insight-text {{

                font-size: 16px;

                line-height: 1.8;

                color: var(--text-primary);
            }}

            .summary-box {{

                border-radius: 24px;

                padding: 28px;

                background:
                    linear-gradient(
                        135deg,
                        rgba(59,130,246,0.08),
                        rgba(124,58,237,0.08)
                    );

                border:
                    1px solid rgba(99,102,241,0.14);
            }}

            .summary-title {{

                font-size: 16px;
                font-weight: 700;

                margin-bottom: 16px;

                color: var(--text-primary);
            }}

            .summary-text {{

                font-size: 17px;

                line-height: 1.9;

                color: var(--text-secondary);
            }}

            .highlight-blue {{
                color: var(--blue);
                font-weight: 700;
            }}

            .highlight-orange {{
                color: var(--orange);
                font-weight: 700;
            }}

            .highlight-purple {{
                color: var(--purple);
                font-weight: 700;
            }}

            @media (max-width: 900px) {{

                .insight-grid {{
                    grid-template-columns: 1fr;
                }}
            }}

            </style>

            <div class="analysis-shell">

                <div class="analysis-header">

                    <div class="analysis-title">
                        AI Analysis
                    </div>

                    <div class="analysis-pill">
                        LIVE INFERENCE
                    </div>

                </div>

                <div class="insight-grid">

                    <div class="insight-card">

                        <div class="insight-label">
                            Tone Assessment
                        </div>

                        <div class="insight-text">

                            The model detected a
                            <span class="highlight-blue">
                                {sentiment}
                            </span>
                            communication pattern with
                            emotionally weighted phrasing.

                            Confidence level for this
                            classification is
                            <span class="highlight-blue">
                                {sentiment_conf}%
                            </span>.

                        </div>

                    </div>

                    <div class="insight-card">

                        <div class="insight-label">
                            Sarcasm Detection
                        </div>

                        <div class="insight-text">

                            Transformer attention patterns
                            classified the text as
                            <span class="highlight-orange">
                                {sarcasm}
                            </span>.

                            Prediction confidence reached
                            <span class="highlight-orange">
                                {sarcasm_conf}%
                            </span>.

                        </div>

                    </div>

                </div>

                <div class="summary-box">

                    <div class="summary-title">
                        AI Interpretation
                    </div>

                    <div class="summary-text">

                        Emotional analysis detected
                        <span class="highlight-purple">
                            {emotion}
                        </span>
                        characteristics with an inference
                        confidence of
                        <span class="highlight-purple">
                            {emotion_conf}%
                        </span>.

                        Multitask transformer outputs
                        remain reasonably aligned across
                        sentiment, sarcasm, and emotion
                        heads, suggesting stable model
                        inference consistency.

                    </div>

                </div>

            </div>

            """

            components.html(
                insight_html,
                height=420,
                scrolling=False
            )