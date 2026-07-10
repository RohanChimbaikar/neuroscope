import streamlit as st
from components.sidebar import render_sidebar_navigation
from styles.theme import PAGE_TITLE, PAGE_LAYOUT, MAIN_TITLE, MAIN_CAPTION
from views.single_prediction import render as render_single_prediction
from views.csv_batch import render as render_csv_batch
from views.model_comparison import render as render_model_comparison
from views.batch_model_comparison import render as render_batch_model_comparison
from views.reddit_intelligence import render as render_reddit_intelligence
from views.about import render as render_about


st.set_page_config(
    page_title=PAGE_TITLE,
    layout=PAGE_LAYOUT
)


st.title(MAIN_TITLE)

st.caption(MAIN_CAPTION)

sidebar_model, page = render_sidebar_navigation()

st.session_state.selected_model = sidebar_model

if page == "Single Prediction":
    render_single_prediction()
elif page == "CSV Batch Analysis":
    render_csv_batch()
elif page == "Model Comparison":
    render_model_comparison()
elif page == "Batch Model Comparison":
    render_batch_model_comparison()
elif page == "Reddit Intelligence":
    render_reddit_intelligence()
elif page == "About":
    render_about()