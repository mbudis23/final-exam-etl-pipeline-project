import torch
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from tqdm import tqdm

# Mendapatkan path model
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "../../models/indobert_2024-11-19_14-31-19")
normalized_path = os.path.realpath(file_path)

print(f"Path model: {normalized_path}")

# Periksa apakah model directory ada
if not os.path.exists(normalized_path):
    raise FileNotFoundError(f"Model directory not found: {normalized_path}")


def label_sentiment(df, text_column="Tweet", batch_size=32):
    """
    Melabeli sentimen dari kolom teks pada DataFrame menggunakan model BERT.

    Parameters:
    - df (pd.DataFrame): DataFrame yang memiliki kolom teks (default: 'Tweet').
    - text_column (str): Nama kolom yang berisi teks untuk diproses (default: 'Tweet').
    - batch_size (int): Jumlah sampel yang diproses dalam satu batch (default: 32).

    Returns:
    - pd.DataFrame: DataFrame dengan kolom 'sentiment' berisi label prediksi.
    """
    # Load model dan tokenizer dari direktori lokal
    model_dir = normalized_path
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    # Pilih perangkat (GPU jika tersedia, jika tidak gunakan CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # Validasi kolom teks
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame")

    # List untuk menyimpan hasil prediksi
    predictions = []

    # Proses data dalam batch
    texts = df[text_column].tolist()
    for i in tqdm(range(0, len(texts), batch_size), desc="Processing batches"):
        batch_texts = texts[i : i + batch_size]

        # Tokenisasi batch
        encoded_batch = tokenizer(
            batch_texts,
            max_length=128,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        # Pindahkan data ke perangkat
        input_ids = encoded_batch["input_ids"].to(device)
        attention_mask = encoded_batch["attention_mask"].to(device)

        # Inferensi model
        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits

        # Ambil label prediksi
        batch_predictions = torch.argmax(logits, dim=1).cpu().tolist()
        predictions.extend(batch_predictions)

    # Tambahkan kolom 'sentiment' ke DataFrame
    df["sentiment"] = predictions
    return df
