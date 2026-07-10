import streamlit as st
import pandas as pd
from utils.charts import sentiment_chart, sarcasm_chart, emotion_chart


def render_analytics_charts(results_df):
    st.plotly_chart(
        sentiment_chart(results_df),
        use_container_width=True
    )

    st.plotly_chart(
        sarcasm_chart(results_df),
        use_container_width=True
    )

    st.plotly_chart(
        emotion_chart(results_df),
        use_container_width=True
    )