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

    ids = pd.to_numeric(df["id"], errors="coerce").dropna()
    if ids.empty:
        return 1

    return int(ids.max()) + 1


def delete_last_entry() -> dict | None:
    df = load_data()
    if df.empty:
        return None

    df["id_num"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.sort_values("id_num")
    removed = df.iloc[-1].to_dict()
    df = df.iloc[:-1].drop(columns=["id_num"])
    save_data(df)
    removed.pop("id_num", None)
    return removed


def delete_entry_by_description(description: str) -> dict | None:
    df = load_data()
    if df.empty:
        return None

    df["descricao"] = df["descricao"].astype(str)
    df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

    matches = df[df["descricao"].str.lower().str.contains(description.lower(), na=False)]
    if matches.empty:
        return None

    matches = matches.sort_values("id_num")
    idx = matches.index[-1]
    removed = df.loc[idx].to_dict()
    df = df.drop(index=idx).drop(columns=["id_num"])
    save_data(df)
    removed.pop("id_num", None)
    return removed


def update_entry_value_by_description(description: str, new_value: float) -> dict | None:
    df = load_data()
    if df.empty:
        return None

    df["descricao"] = df["descricao"].astype(str)
    df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

    matches = df[df["descricao"].str.lower().str.contains(description.lower(), na=False)]
    if matches.empty:
        return None

    matches = matches.sort_values("id_num")
    idx = matches.index[-1]
    df.loc[idx, "valor"] = new_value

    updated = df.loc[idx].to_dict()
    df = df.drop(columns=["id_num"])
    save_data(df)
    updated.pop("id_num", None)
    return updated


def update_entry_category_by_description(description: str, new_category: str) -> dict | None:
    df = load_data()
    if df.empty:
        return None

    df["descricao"] = df["descricao"].astype(str)
    df["id_num"] = pd.to_numeric(df["id"], errors="coerce")

    matches = df[df["descricao"].str.lower().str.contains(description.lower(), na=False)]
    if matches.empty:
        return None

    matches = matches.sort_values("id_num")
    idx = matches.index[-1]
    df.loc[idx, "categoria"] = new_category.strip().lower()

    updated = df.loc[idx].to_dict()
    df = df.drop(columns=["id_num"])
    save_data(df)
    updated.pop("id_num", None)
    return updated