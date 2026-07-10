import streamlit as st
import pandas as pd
from utils.inference import predict_text
from utils.charts import emotion_chart
from components.comparison_tables import render_agreement_metrics


def render():
    st.header(
        "Batch Transformer Comparison"
    )

    st.markdown(
        """
        Compare RoBERTa and DeBERTa predictions
        across an entire dataset.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        key="comparison_csv"
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        if "text" not in df.columns:
            st.error(
                "CSV must contain a 'text' column"
            )
        else:
            st.subheader("Dataset Preview")
            st.dataframe(df.head())

            roberta_outputs = []
            deberta_outputs = []

            progress_bar = st.progress(0)

            for idx, row in df.iterrows():
                text = str(row["text"])

                roberta_pred = predict_text(
                    text,
                    "RoBERTa"
                )

                deberta_pred = predict_text(
                    text,
                    "DeBERTa"
                )

                roberta_outputs.append(
                    roberta_pred
                )

                deberta_outputs.append(
                    deberta_pred
                )

                progress_bar.progress(
                    (idx + 1) / len(df)
                )

            roberta_df = pd.DataFrame(
                roberta_outputs
            )

            deberta_df = pd.DataFrame(
                deberta_outputs
            )

            comparison_df = pd.DataFrame({
                "text":
                df["text"],

                "roberta_sentiment":
                roberta_df["sentiment"],

                "deberta_sentiment":
                deberta_df["sentiment"],

                "roberta_sarcasm":
                roberta_df["sarcasm"],

                "deberta_sarcasm":
                deberta_df["sarcasm"],

                "roberta_emotion":
                roberta_df["emotion"],

                "deberta_emotion":
                deberta_df["emotion"]
            })

            st.subheader(
                "Transformer Agreement Metrics"
            )

            render_agreement_metrics(comparison_df)

            st.divider()

            st.subheader(
                "Disagreement Analysis"
            )

            disagreement_df = comparison_df[
                (
                    comparison_df["roberta_sentiment"]
                    !=
                    comparison_df["deberta_sentiment"]
                )
                |
                (
                    comparison_df["roberta_sarcasm"]
                    !=
                    comparison_df["deberta_sarcasm"]
                )
                |
                (
                    comparison_df["roberta_emotion"]
                    !=
                    comparison_df["deberta_emotion"]
                )
            ]

            st.dataframe(
                disagreement_df,
                use_container_width=True
            )

            st.divider()

            st.subheader(
                "RoBERTa Emotion Distribution"
            )

            st.plotly_chart(
                emotion_chart(roberta_df),
                use_container_width=True
            )

            st.subheader(
                "DeBERTa Emotion Distribution"
            )

            st.plotly_chart(
                emotion_chart(deberta_df),
                use_container_width=True
            )

            st.divider()

            csv = comparison_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Comparison CSV",
                data=csv,
                file_name="transformer_comparison.csv",
                mime="text/csv"
            )