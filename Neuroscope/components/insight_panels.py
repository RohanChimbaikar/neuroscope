import streamlit as st


def render_insight_sentiment_agreement(roberta_result, deberta_result):
    if roberta_result["sentiment"] == deberta_result["sentiment"]:
        st.success(
            f"""
            Both models agree on sentiment:
            {roberta_result["sentiment"]}
            """
        )
    else:
        st.warning(
            f"""
            Sentiment disagreement detected.

            RoBERTa:
            {roberta_result["sentiment"]}

            DeBERTa:
            {deberta_result["sentiment"]}
            """
        )


def render_insight_sarcasm_agreement(roberta_result, deberta_result):
    if roberta_result["sarcasm"] == deberta_result["sarcasm"]:
        st.success(
            f"""
            Both models agree on sarcasm:
            {roberta_result["sarcasm"]}
            """
        )
    else:
        st.error(
            """
            Sarcasm interpretation differs
            between transformers.
            """
        )


def render_insight_emotion_agreement(roberta_result, deberta_result):
    if roberta_result["emotion"] == deberta_result["emotion"]:
        st.success(
            f"""
            Shared emotional interpretation:
            {roberta_result["emotion"]}
            """
        )
    else:
        st.info(
            f"""
            Emotional interpretation differs.

            RoBERTa:
            {roberta_result["emotion"]}

            DeBERTa:
            {deberta_result["emotion"]}
            """
        )


def render_community_insight(positive_pct, negative_pct, sarcasm_pct, dominant_sentiment, dominant_emotion):
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#111827,#1f2937);padding:24px;border-radius:20px;margin-top:24px;margin-bottom:24px;border:1px solid rgba(255,255,255,0.08);'>

<div style='font-size:24px;font-weight:800;margin-bottom:14px;color:white;'>

Community Insight

</div>

<div style='font-size:17px;line-height:1.9;color:#d1d5db;'>

The Reddit discussion is primarily
characterized by
<b>{dominant_sentiment}</b>
sentiment with strong traces of
<b>{dominant_emotion}</b>.

Approximately
<b>{sarcasm_pct:.1f}%</b>
of analyzed comments exhibit sarcastic
behavior patterns.

Positive engagement:
<b>{positive_pct:.1f}%</b>

Negative engagement:
<b>{negative_pct:.1f}%</b>

</div>

</div>""",
        unsafe_allow_html=True
    )