import streamlit as st
import pandas as pd


def render_model_comparison_metrics(roberta_result, deberta_result):
    top1, top2, top3 = st.columns(3)

    with top1:
        st.metric(
            "RoBERTa Sentiment",
            roberta_result["sentiment"]
        )

        st.metric(
            "DeBERTa Sentiment",
            deberta_result["sentiment"]
        )

    with top2:
        st.metric(
            "RoBERTa Sarcasm",
            roberta_result["sarcasm"]
        )

        st.metric(
            "DeBERTa Sarcasm",
            deberta_result["sarcasm"]
        )

    with top3:
        st.metric(
            "RoBERTa Emotion",
            roberta_result["emotion"]
        )

        st.metric(
            "DeBERTa Emotion",
            deberta_result["emotion"]
        )


def render_detailed_comparison_table(roberta_result, deberta_result):
    comparison_df = pd.DataFrame({
        "Metric": [
            "Sentiment",
            "Sentiment Confidence",
            "Sarcasm",
            "Sarcasm Confidence",
            "Emotion",
            "Emotion Confidence"
        ],
        "RoBERTa": [
            roberta_result["sentiment"],
            round(
                roberta_result["sentiment_conf"],
                4
            ),
            roberta_result["sarcasm"],
            round(
                roberta_result["sarcasm_conf"],
                4
            ),
            roberta_result["emotion"],
            round(
                roberta_result["emotion_conf"],
                4
            )
        ],
        "DeBERTa": [
            deberta_result["sentiment"],
            round(
                deberta_result["sentiment_conf"],
                4
            ),
            deberta_result["sarcasm"],
            round(
                deberta_result["sarcasm_conf"],
                4
            ),
            deberta_result["emotion"],
            round(
                deberta_result["emotion_conf"],
                4
            )
        ]
    })

    st.dataframe(
        comparison_df,
        use_container_width=True
    )


def render_confidence_bar_chart(roberta_result, deberta_result):
    confidence_df = pd.DataFrame({
        "Task": [
            "Sentiment",
            "Sarcasm",
            "Emotion"
        ],
        "RoBERTa": [
            roberta_result["sentiment_conf"],
            roberta_result["sarcasm_conf"],
            roberta_result["emotion_conf"]
        ],
        "DeBERTa": [
            deberta_result["sentiment_conf"],
            deberta_result["sarcasm_conf"],
            deberta_result["emotion_conf"]
        ]
    })

    st.bar_chart(
        confidence_df.set_index("Task")
    )


def render_agreement_metrics(comparison_df):
    sentiment_agreement = (
        comparison_df["roberta_sentiment"]
        == comparison_df["deberta_sentiment"]
    ).mean()

    sarcasm_agreement = (
        comparison_df["roberta_sarcasm"]
        == comparison_df["deberta_sarcasm"]
    ).mean()

    emotion_agreement = (
        comparison_df["roberta_emotion"]
        == comparison_df["deberta_emotion"]
    ).mean()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sentiment Agreement",
            f"{sentiment_agreement:.2%}"
        )

    with col2:
        st.metric(
            "Sarcasm Agreement",
            f"{sarcasm_agreement:.2%}"
        )

    with col3:
        st.metric(
            "Emotion Agreement",
            f"{emotion_agreement:.2%}"
        )