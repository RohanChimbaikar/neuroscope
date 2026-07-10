from utils.inference import predict_text


def run_batch_predictions(df, model_key):
    results = []

    for idx, row in df.iterrows():
        prediction = predict_text(
            str(row["text"]),
            model_key
        )
        results.append(prediction)

    return results


def run_batch_comparison_predictions(df, models=["RoBERTa", "DeBERTa"]):
    all_outputs = {}

    for model_name in models:
        outputs = []
        for idx, row in df.iterrows():
            text = str(row["text"])
            pred = predict_text(text, model_name)
            outputs.append(pred)
        all_outputs[model_name] = outputs

    return all_outputs


def run_reddit_batch_predictions(comments, model_key):
    results = []

    for comment in comments:
        try:
            prediction = predict_text(
                comment,
                model_key
            )
            prediction["comment"] = comment
            results.append(prediction)
        except Exception:
            continue

    return results