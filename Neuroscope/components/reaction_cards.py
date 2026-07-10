import streamlit.components.v1 as components


def render_reaction_card(row):

    emotion = row.get(
        "emotion",
        "neutral"
    ).title()

    sentiment = row.get(
        "sentiment",
        "neutral"
    ).title()

    sarcasm = row.get(
        "sarcasm",
        "not sarcastic"
    ).title()

    confidence = round(
        row.get(
            "emotion_conf",
              0
             ) * 100,
        1
    )

    comment = row.get(
        "comment",
        ""
    )

    # ---------------------------------
    # COLOR SYSTEM
    # ---------------------------------

    emotion_colors = {

        "Love": "#ec4899",
        "Admiration": "#8b5cf6",
        "Gratitude": "#3b82f6",
        "Joy": "#22c55e",
        "Anger": "#ef4444",
        "Sadness": "#64748b",
        "Fear": "#f59e0b",
        "Surprise": "#06b6d4",
        "Neutral": "#94a3b8"
    }

    accent = emotion_colors.get(
        emotion,
        "#6366f1"
    )

    html = f"""

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

    .reaction-card {{

        position: relative;

        overflow: hidden;

        border-radius: 24px;

        padding: 24px;

        margin-bottom: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,0.88),
                rgba(248,250,252,0.96)
            );

        border:
            1px solid rgba(15,23,42,0.06);

        box-shadow:
            0 8px 24px rgba(15,23,42,0.08);
    }}

    @media (prefers-color-scheme: dark) {{

        .reaction-card {{

            background:
                linear-gradient(
                    135deg,
                    rgba(17,24,39,0.92),
                    rgba(15,23,42,0.96)
                );

            border:
                1px solid rgba(255,255,255,0.06);

            box-shadow:
                0 8px 24px rgba(0,0,0,0.24);
        }}
    }}

    .reaction-top {{

        display: flex;
        align-items: flex-start;
        justify-content: space-between;

        gap: 18px;

        margin-bottom: 18px;
    }}

    .reaction-left {{

        flex: 1;
    }}

    .emotion-row {{

        display: flex;
        align-items: center;

        gap: 12px;

        margin-bottom: 10px;
    }}

    .emotion-dot {{

        width: 14px;
        height: 14px;

        border-radius: 50%;

        background: {accent};

        box-shadow:
            0 0 18px {accent};
    }}

    .emotion-title {{

        font-size: 28px;
        font-weight: 800;

        letter-spacing: -0.04em;

        color: #0f172a;
    }}

    @media (prefers-color-scheme: dark) {{

        .emotion-title {{
            color: #f8fafc;
        }}
    }}

    .meta-row {{

        display: flex;
        flex-wrap: wrap;

        gap: 10px;
    }}

    .meta-pill {{

        padding:
            7px 12px;

        border-radius: 999px;

        font-size: 12px;
        font-weight: 700;

        background:
            rgba(99,102,241,0.08);

        color:
            #475569;
    }}

    @media (prefers-color-scheme: dark) {{

        .meta-pill {{

            background:
                rgba(255,255,255,0.06);

            color:
                #cbd5e1;
        }}
    }}

    .strength-pill {{

        flex-shrink: 0;

        padding:
            10px 14px;

        border-radius: 999px;

        background: {accent};

        color: white;

        font-size: 13px;
        font-weight: 700;
    }}

    .comment-box {{

        position: relative;

        border-radius: 18px;

        padding: 18px;

        background:
            rgba(15,23,42,0.04);

        border:
            1px solid rgba(148,163,184,0.12);
    }}

    @media (prefers-color-scheme: dark) {{

        .comment-box {{

            background:
                rgba(255,255,255,0.04);

            border:
                1px solid rgba(255,255,255,0.05);
        }}
    }}

    .comment-text {{

        font-size: 15px;

        line-height: 1.8;

        color: #334155;

        word-break: break-word;
    }}

    @media (prefers-color-scheme: dark) {{

        .comment-text {{
            color: #e2e8f0;
        }}
    }}

    </style>

    <div class="reaction-card">

        <div class="reaction-top">

            <div class="reaction-left">

                <div class="emotion-row">

                    <div class="emotion-dot"></div>

                    <div class="emotion-title">
                        {emotion}
                    </div>

                </div>

                <div class="meta-row">

                    <div class="meta-pill">
                        {sentiment} Sentiment
                    </div>

                    <div class="meta-pill">
                        {sarcasm}
                    </div>

                </div>

            </div>

            <div class="strength-pill">
                {confidence}%
            </div>

        </div>

        <div class="comment-box">

            <div class="comment-text">
                "{comment}"
            </div>

        </div>

    </div>
    """

    components.html(
        html,
        height=220,
        scrolling=False
    )