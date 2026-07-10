def calculate_community_metrics(results_df):
    positive_pct = (
        (results_df["sentiment"] == "positive").mean()
        * 100
    )

    negative_pct = (
        (results_df["sentiment"] == "negative").mean()
        * 100
    )

    sarcasm_pct = (
        (results_df["sarcasm"] == "sarcastic").mean()
        * 100
    )

    dominant_emotion = results_df["emotion"].mode()[0]
    dominant_sentiment = results_df["sentiment"].mode()[0]

    return {
        "positive_pct": positive_pct,
        "negative_pct": negative_pct,
        "sarcasm_pct": sarcasm_pct,
        "dominant_emotion": dominant_emotion,
        "dominant_sentiment": dominant_sentiment
    }


EMOTION_WEIGHT_MAP = {
    "neutral": 0.2,
    "admiration": 0.8,
    "joy": 0.9,
    "love": 1.0,
    "gratitude": 0.9,
    "excitement": 1.0,
    "anger": 1.0,
    "annoyance": 0.9,
    "disgust": 1.0,
    "sadness": 0.9,
    "fear": 0.8,
    "surprise": 0.7,
    "confusion": 0.7,
    "curiosity": 0.6
}


def prepare_reaction_df(results_df):
    reaction_df = results_df.copy()
    reaction_df = reaction_df.drop_duplicates(subset=["comment"])
    reaction_df = reaction_df[reaction_df["comment"].str.len() > 20]
    reaction_df["emotion_weight"] = reaction_df["emotion"].map(
        EMOTION_WEIGHT_MAP
    ).fillna(0.6)
    reaction_df["reaction_score"] = (
        reaction_df["emotion_conf"] *
        reaction_df["emotion_weight"]
    )
    reaction_df.loc[
        reaction_df["sarcasm"] == "sarcastic",
        "reaction_score"
    ] *= 1.15
    reaction_df = reaction_df.sort_values(
        "reaction_score",
        ascending=False
    )
    return reaction_df


def select_diverse_reactions(reaction_df, max_count=6):
    selected_rows = []
    used_emotions = set()

    for _, row in reaction_df.iterrows():
        emotion = row["emotion"]
        if emotion not in used_emotions:
            selected_rows.append(row)
            used_emotions.add(emotion)
        if len(selected_rows) >= max_count:
            break

    if len(selected_rows) < max_count:
        for _, row in reaction_df.iterrows():
            if len(selected_rows) >= max_count:
                break
            exists = any(
                existing["comment"] == row["comment"]
                for existing in selected_rows
            )
            if not exists:
                selected_rows.append(row)

    return selected_rows