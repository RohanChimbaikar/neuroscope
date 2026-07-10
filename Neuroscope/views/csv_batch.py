import streamlit as st
import pandas as pd
from utils.inference import predict_text
from utils.charts import sentiment_chart, sarcasm_chart, emotion_chart


def render():
    st.header("CSV Batch Analysis")

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.subheader("Preview")
        st.dataframe(df.head())

        if "text" not in df.columns:
            st.error(
                "CSV must contain a column named 'text'"
            )
        else:
            results = []
            progress_bar = st.progress(0)

            for idx, row in df.iterrows():
                prediction = predict_text(
                    str(row["text"]),
                    st.session_state.get("selected_model", "DeBERTa")
                )
                results.append(prediction)
                progress_bar.progress(
                    (idx + 1) / len(df)
                )

            results_df = pd.DataFrame(results)
            final_df = pd.concat(
                [df, results_df],
                axis=1
            )

            st.subheader("Predictions")
            st.dataframe(final_df)

            st.subheader("Analytics Dashboard")
            st.plotly_chart(
                sentiment_chart(final_df),
                use_container_width=True
            )
            st.plotly_chart(
                sarcasm_chart(final_df),
                use_container_width=True
            )
            st.plotly_chart(
                emotion_chart(final_df),
                use_container_width=True
            )

            csv = final_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name="neuroscope_predictions.csv",
                mime="text/csv"
            )