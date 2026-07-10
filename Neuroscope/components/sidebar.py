import streamlit as st


def render_sidebar_navigation():
    sidebar_model = st.sidebar.selectbox(
        "Select Model",
        [
            "DeBERTa",
            "RoBERTa"
        ]
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Single Prediction",
            "CSV Batch Analysis",
            "Model Comparison",
            "Batch Model Comparison",
            "Reddit Intelligence",
            "About"
        ]
    )

    return sidebar_model, page