import streamlit as st
from utils.inference import predict_text
from components.comparison_tables import (
    render_model_comparison_metrics,
    render_detailed_comparison_table,
    render_confidence_bar_chart
)
from components.insight_panels import (
    render_insight_sentiment_agreement,
    render_insight_sarcasm_agreement,
    render_insight_emotion_agreement
)


def render():
    st.header(
        "Advanced Transformer Comparison"
    )

    st.markdown(
        """
        Compare RoBERTa and DeBERTa predictions,
        confidence behavior, sarcasm handling,
        and emotional interpretation.
        """
    )

    text = st.text_area(
        "Enter text for deep comparison",
        height=220
    )

    if st.button("Run Advanced Comparison"):
        if text.strip() == "":
            st.warning("Please enter text")
        else:
            with st.spinner(
                "Running transformer inference..."
            ):
                roberta_result = predict_text(
                    text,
                    "RoBERTa"
                )

                deberta_result = predict_text(
                    text,
                    "DeBERTa"
                )

            st.subheader(
                "Prediction Summary"
            )

            render_model_comparison_metrics(roberta_result, deberta_result)

            st.divider()

            st.subheader(
                "Detailed Confidence Analysis"
            )

            render_detailed_comparison_table(roberta_result, deberta_result)

            st.divider()

            st.subheader(
                "Comparative Transformer Insights"
            )

            render_insight_sentiment_agreement(roberta_result, deberta_result)
            render_insight_sarcasm_agreement(roberta_result, deberta_result)
            render_insight_emotion_agreement(roberta_result, deberta_result)

            st.divider()

            st.subheader(
                "Confidence Competition"
            )

            render_confidence_bar_chart(roberta_result, deberta_result)

            st.divider()

            with st.expander(
                "Raw Transformer Outputs"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(
                        "RoBERTa Output"
                    )

                    st.json(roberta_result)

                with col2:
                    st.subheader(
                        "DeBERTa Output"
                    )

                    st.json(deberta_result)