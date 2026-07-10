import streamlit as st


def render():
    st.header("About NeuroScope")

    st.markdown(
        '''
        NeuroScope is a multitask transformer NLP system
        developed for MSc research.

        Core Tasks:
        - Sentiment Analysis
        - Sarcasm Detection
        - Emotion Classification

        Transformer Models:
        - RoBERTa Multitask Model
        - Final Combined DeBERTa Model

        Research Features:
        - Comparative Transformer Evaluation
        - Multitask Learning
        - Calibrated Sarcasm Intelligence
        - CSV Batch Analytics
        - Interactive NLP Dashboard
        '''
    )