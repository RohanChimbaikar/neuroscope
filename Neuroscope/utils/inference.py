import torch
import torch.nn as nn

from transformers import (
    AutoTokenizer,
    AutoModel
)

from utils.labels import (
    SENTIMENT_LABELS,
    SARCASM_LABELS,
    EMOTION_LABELS
)


# =====================================================
# DEVICE
# =====================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# =====================================================
# ROBERTA MODEL
# =====================================================

class RoBERTaMultiTaskModel(nn.Module):

    def __init__(self):

        super().__init__()

        self.encoder = AutoModel.from_pretrained(
            "roberta-base"
        )

        hidden_size = (
            self.encoder.config.hidden_size
        )

        self.dropout = nn.Dropout(0.3)

        self.sentiment_head = nn.Linear(
            hidden_size,
            3
        )

        self.sarcasm_head = nn.Linear(
            hidden_size,
            2
        )

        self.emotion_head = nn.Linear(
            hidden_size,
            28
        )

    def forward(
        self,
        input_ids,
        attention_mask
    ):

        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        cls_output = (
            outputs.last_hidden_state[:, 0]
        )

        cls_output = self.dropout(
            cls_output
        )

        sentiment_logits = (
            self.sentiment_head(cls_output)
        )

        sarcasm_logits = (
            self.sarcasm_head(cls_output)
        )

        emotion_logits = (
            self.emotion_head(cls_output)
        )

        return (
            sentiment_logits,
            sarcasm_logits,
            emotion_logits
        )


# =====================================================
# DEBERTA MODEL
# =====================================================

class DeBERTaMultiTaskModel(nn.Module):

    def __init__(self):

        super().__init__()

        self.encoder = AutoModel.from_pretrained(
            "microsoft/deberta-base"
        )

        hidden_size = (
            self.encoder.config.hidden_size
        )

        self.dropout = nn.Dropout(0.3)

        # =========================
        # SENTIMENT
        # =========================

        self.sentiment_head = nn.Sequential(

            nn.Linear(hidden_size, 256),

            nn.ReLU(),

            nn.Dropout(0.3),

            nn.Linear(256, 3)
        )

        # =========================
        # SARCASM
        # =========================

        self.sarcasm_head = nn.Sequential(

            nn.Linear(hidden_size, 512),

            nn.LayerNorm(512),

            nn.ReLU(),

            nn.Dropout(0.3),

            nn.Linear(512, 256),

            nn.ReLU(),

            nn.Dropout(0.2),

            nn.Linear(256, 2)
        )

        # =========================
        # EMOTION
        # =========================

        self.emotion_head = nn.Sequential(

            nn.Linear(hidden_size, 512),

            nn.ReLU(),

            nn.Dropout(0.3),

            nn.Linear(512, 28)
        )

    def forward(
        self,
        input_ids,
        attention_mask
    ):

        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        cls_output = (
            outputs.last_hidden_state[:, 0]
        )

        cls_output = self.dropout(
            cls_output
        )

        sentiment_logits = (
            self.sentiment_head(cls_output)
        )

        sarcasm_logits = (
            self.sarcasm_head(cls_output)
        )

        emotion_logits = (
            self.emotion_head(cls_output)
        )

        return (
            sentiment_logits,
            sarcasm_logits,
            emotion_logits
        )


# =====================================================
# CACHE
# =====================================================

loaded_models = {}
loaded_tokenizers = {}


# =====================================================
# LOAD MODEL
# =====================================================

def load_model(model_key):

    if model_key in loaded_models:

        return (
            loaded_models[model_key],
            loaded_tokenizers[model_key]
        )

    # =========================================
    # ROBERTA
    # =========================================

    if model_key == "RoBERTa":

        tokenizer = (
            AutoTokenizer.from_pretrained(
                "roberta-base"
            )
        )

        model = RoBERTaMultiTaskModel()

        checkpoint_path = (
            "models/"
            "neuroscope_improved_multitask_roberta/"
            "model.pt"
        )

    # =========================================
    # DEBERTA
    # =========================================

    else:

        tokenizer = (
            AutoTokenizer.from_pretrained(
                "microsoft/deberta-base"
            )
        )

        model = DeBERTaMultiTaskModel()

        checkpoint_path = (
            "models/"
            "neuroscope_final_combined_deberta/"
            "final_combined_model.pt"
        )

    # =========================================
    # LOAD CHECKPOINT
    # =========================================

    checkpoint = torch.load(
        checkpoint_path,
        map_location=DEVICE
    )

    # =========================================
    # LOAD STATE DICT
    # =========================================

    if isinstance(checkpoint, dict):

        if "model_state_dict" in checkpoint:

            model.load_state_dict(
                checkpoint["model_state_dict"]
            )

        elif "state_dict" in checkpoint:

            model.load_state_dict(
                checkpoint["state_dict"]
            )

        elif "model" in checkpoint:

            model.load_state_dict(
                checkpoint["model"]
            )

        else:

            model.load_state_dict(
                checkpoint
            )

    else:

        model.load_state_dict(
            checkpoint
        )

    model.to(DEVICE)

    model.eval()

    loaded_models[model_key] = model

    loaded_tokenizers[model_key] = tokenizer

    return model, tokenizer


# =====================================================
# PREDICTION
# =====================================================

def predict_text(
    text,
    model_key="DeBERTa"
):

    model, tokenizer = load_model(
        model_key
    )

    encoding = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=128,
        return_tensors="pt"
    )

    input_ids = (
        encoding["input_ids"].to(DEVICE)
    )

    attention_mask = (
        encoding["attention_mask"].to(DEVICE)
    )

    with torch.no_grad():

        (
            sentiment_logits,
            sarcasm_logits,
            emotion_logits
        ) = model(
            input_ids,
            attention_mask
        )

        sentiment_probs = torch.softmax(
            sentiment_logits,
            dim=1
        )

        sarcasm_probs = torch.softmax(
            sarcasm_logits,
            dim=1
        )

        emotion_probs = torch.softmax(
            emotion_logits,
            dim=1
        )

    sentiment_pred = torch.argmax(
        sentiment_probs,
        dim=1
    ).item()

    sarcasm_pred = torch.argmax(
        sarcasm_probs,
        dim=1
    ).item()

    emotion_pred = torch.argmax(
        emotion_probs,
        dim=1
    ).item()

    return {

        "sentiment":
        SENTIMENT_LABELS.get(
            sentiment_pred,
            str(sentiment_pred)
        ),

        "sentiment_conf":
        float(
            sentiment_probs[0][sentiment_pred]
        ),

        "sarcasm":
        SARCASM_LABELS.get(
            sarcasm_pred,
            str(sarcasm_pred)
        ),

        "sarcasm_conf":
        float(
            sarcasm_probs[0][sarcasm_pred]
        ),

        "emotion":
        EMOTION_LABELS.get(
            emotion_pred,
            str(emotion_pred)
        ),

        "emotion_conf":
        float(
            emotion_probs[0][emotion_pred]
        )
    }