from __future__ import annotations

from datetime import datetime
import pandas as pd

from storage import load_data


def _load_current_month() -> pd.DataFrame:
    df = load_data()
    if df.empty:
        return df

    df["data_evento"] = pd.to_datetime(df["data_evento"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["tipo"] = df["tipo"].astype(str).str.strip().str.lower()
    df["categoria"] = df["categoria"].astype(str).str.strip().str.lower()

    now = datetime.now()

    return df[
        df["data_evento"].notna() &
        (df["data_evento"].dt.month == now.month) &
        (df["data_evento"].dt.year == now.year)
    ]


def total_expenses_month() -> float:
    df = _load_current_month()
    if df.empty:
        return 0.0
    return float(df[df["tipo"] == "saida"]["valor"].sum())


def total_income_month() -> float:
    df = _load_current_month()
    if df.empty:
        return 0.0
    return float(df[df["tipo"] == "entrada"]["valor"].sum())


def balance_month() -> float:
    return total_income_month() - total_expenses_month()


def total_by_category_month(category: str) -> float:
    df = _load_current_month()
    if df.empty:
        return 0.0

    normalized_category = category.strip().lower()
    filtered = df[
        (df["tipo"] == "saida") &
        (df["categoria"] == normalized_category)
    ]
    return float(filtered["valor"].sum())


def monthly_summary() -> dict:
    df = _load_current_month()
    if df.empty:
        return {
            "entradas": 0.0,
            "saidas": 0.0,
            "saldo": 0.0,
            "maior_categoria": "nenhuma",
        }

    expenses = df[df["tipo"] == "saida"]
    by_category = expenses.groupby("categoria")["valor"].sum()

    major_category = "nenhuma"
    if not by_category.empty:
        major_category = str(by_category.idxmax())

    entradas = float(df[df["tipo"] == "entrada"]["valor"].sum())
    saidas = float(expenses["valor"].sum())

    return {
        "entradas": entradas,
        "saidas": saidas,
        "saldo": entradas - saidas,
        "maior_categoria": major_category,
    }