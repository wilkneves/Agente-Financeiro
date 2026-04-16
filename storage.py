from __future__ import annotations

from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError

DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "lancamentos.csv"

COLUMNS = [
    "id",
    "data_evento",
    "data_registro",
    "tipo",
    "valor",
    "categoria",
    "descricao",
    "forma_pagamento",
    "observacoes",
    "mensagem_original",
]


def ensure_storage() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    if not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)


def load_data() -> pd.DataFrame:
    ensure_storage()

    try:
        df = pd.read_csv(CSV_FILE)
    except EmptyDataError:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)
        return df

    # Garante que, mesmo se o arquivo estiver estranho, as colunas existam
    if df.empty and list(df.columns) != COLUMNS:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

    return df


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(CSV_FILE, index=False)


def append_entry(entry: dict) -> None:
    df = load_data()
    new_row = pd.DataFrame([entry], columns=COLUMNS)
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)


def next_id() -> int:
    df = load_data()
    if df.empty:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").max()) + 1