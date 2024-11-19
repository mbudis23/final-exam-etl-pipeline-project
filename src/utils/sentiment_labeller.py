import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

def label_sentiment(df, model_path, text_column="Text", batch_size=32):
    """
    Melabeli sentimen dari kolom teks pada DataFrame menggunakan model BERT.

    Parameters:
    - df (pd.DataFrame): DataFrame yang memiliki kolom teks.
    - model_path (str): Path ke model lokal.
    - text_column (str): Nama kolom yang berisi teks untuk diproses.
    - batch_size (int): Jumlah sampel yang diproses dalam satu batch.

    Returns:
    - pd.DataFrame: DataFrame dengan kolom tambahan 'sentiment' berisi label prediksi.
    """
    # Load model dan tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Pilih perangkat (GPU jika tersedia, jika tidak gunakan CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # Validasi kolom teks
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame")

    # Proses data dalam batch
    texts = df[text_column].tolist()
    predictions = []

    for i in tqdm(range(0, len(texts), batch_size), desc="Processing batches"):
        batch_texts = texts[i:i + batch_size]

        # Tokenisasi batch
        encoded_batch = tokenizer(
            batch_texts,
            max_length=128,
            padding=True,
            truncation=True,
            return_tensors="pt"
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
    df["Sentiment"] = predictions
    return df
