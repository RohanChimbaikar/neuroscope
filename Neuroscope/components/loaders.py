import streamlit as st


def render_progress_loader(iterable, progress_text="Processing..."):
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    for idx, item in enumerate(iterable):
        status_text.markdown(
            f"""
            {progress_text}
            {idx + 1} / {len(iterable)}
            """
        )
        results.append(item)
        progress_bar.progress((idx + 1) / len(iterable))

    status_text.empty()
    return results, progress_bar


def render_spinner(text="Loading..."):
    return st.spinner(text)