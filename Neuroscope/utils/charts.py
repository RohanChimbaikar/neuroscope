import plotly.express as px


# ---------------------------------
# COMMON CLEAN MODERN THEME
# ---------------------------------

def _apply_modern_theme(fig):

    fig.update_layout(

        template="plotly_white",

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, sans-serif",
            color="#334155",
            size=14
        ),

        title=dict(
            x=0,
            xanchor="left",
            font=dict(
                size=24,
                family="Inter, sans-serif",
                color="#0f172a"
            )
        ),

        margin=dict(
            l=10,
            r=10,
            t=70,
            b=10
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,

            bgcolor="rgba(0,0,0,0)",

            font=dict(
                size=13,
                color="#475569"
            )
        ),

        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="rgba(15,23,42,0.08)",
            font_size=13,
            font_family="Inter",
            font_color="#0f172a"
        )
    )

    fig.update_xaxes(

        showgrid=False,

        zeroline=False,

        linecolor="rgba(148,163,184,0.18)",

        tickfont=dict(
            size=13,
            color="#475569"
        )
    )

    fig.update_yaxes(

        gridcolor="rgba(148,163,184,0.12)",

        zeroline=False,

        tickfont=dict(
            size=13,
            color="#475569"
        )
    )

    return fig


# ---------------------------------
# EMOTION DISTRIBUTION
# ---------------------------------

def emotion_chart(df):

    counts = (
        df["emotion"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "emotion",
        "count"
    ]

    fig = px.bar(
        counts,

        x="emotion",
        y="count",

        text="count",

        title="Emotion Distribution",

        color="emotion",

        color_discrete_sequence=[
            "#8b5cf6",
            "#a855f7",
            "#c084fc",
            "#7c3aed",
            "#6d28d9"
        ]
    )

    fig.update_traces(

        marker_line_width=0,

        textposition="outside",

        hovertemplate=
        "<b>%{x}</b><br>" +
        "Count: %{y}<extra></extra>"
    )

    fig.update_layout(

        height=420,

        xaxis_title="",
        yaxis_title="Texts",

        showlegend=False
    )

    return _apply_modern_theme(fig)


# ---------------------------------
# SENTIMENT DISTRIBUTION
# ---------------------------------

def sentiment_chart(df):

    counts = (
        df["sentiment"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "sentiment",
        "count"
    ]

    fig = px.pie(
        counts,

        names="sentiment",
        values="count",

        hole=0.62,

        title="Sentiment Distribution",

        color="sentiment",

        color_discrete_map={

            "positive": "#3b82f6",
            "negative": "#ef4444",
            "neutral": "#94a3b8"
        }
    )

    fig.update_traces(

        textposition="inside",

        textfont_size=14,

        hovertemplate=
        "<b>%{label}</b><br>" +
        "Count: %{value}<br>" +
        "Share: %{percent}<extra></extra>",

        marker=dict(
            line=dict(
                color="white",
                width=2
            )
        )
    )

    fig.update_layout(

        height=420,

        showlegend=True
    )

    return _apply_modern_theme(fig)


# ---------------------------------
# SARCASM DISTRIBUTION
# ---------------------------------

def sarcasm_chart(df):

    counts = (
        df["sarcasm"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "sarcasm",
        "count"
    ]

    fig = px.bar(
        counts,

        x="sarcasm",
        y="count",

        text="count",

        title="Sarcasm Distribution",

        color="sarcasm",

        color_discrete_map={

            "sarcastic": "#f59e0b",
            "not sarcastic": "#3b82f6"
        }
    )

    fig.update_traces(

        marker_line_width=0,

        textposition="outside",

        hovertemplate=
        "<b>%{x}</b><br>" +
        "Count: %{y}<extra></extra>"
    )

    fig.update_layout(

        height=420,

        xaxis_title="",
        yaxis_title="Texts",

        showlegend=False
    )

    return _apply_modern_theme(fig)