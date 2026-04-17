from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd

from storage import load_data


def _prepare_df() -> pd.DataFrame:
    df = load_data()
    if df.empty:
        return df

    df["data_evento"] = pd.to_datetime(df["data_evento"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["tipo"] = df["tipo"].astype(str).str.strip().str.lower()
    df["categoria"] = df["categoria"].astype(str).str.strip().str.lower()
    df["descricao"] = df["descricao"].astype(str).str.strip()

    return df[df["data_evento"].notna()]


def _load_current_month() -> pd.DataFrame:
    df = _prepare_df()
    if df.empty:
        return df

    now = datetime.now()

    return df[
        (df["data_evento"].dt.month == now.month) &
        (df["data_evento"].dt.year == now.year)
    ]


def _filter_by_day(target_date) -> pd.DataFrame:
    df = _prepare_df()
    if df.empty:
        return df

    return df[df["data_evento"].dt.date == target_date]


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


def total_expenses_today() -> float:
    today = datetime.now().date()
    df = _filter_by_day(today)
    if df.empty:
        return 0.0
    return float(df[df["tipo"] == "saida"]["valor"].sum())


def total_expenses_yesterday() -> float:
    yesterday = datetime.now().date() - timedelta(days=1)
    df = _filter_by_day(yesterday)
    if df.empty:
        return 0.0
    return float(df[df["tipo"] == "saida"]["valor"].sum())


def total_income_today() -> float:
    today = datetime.now().date()
    df = _filter_by_day(today)
    if df.empty:
        return 0.0
    return float(df[df["tipo"] == "entrada"]["valor"].sum())


def total_income_yesterday() -> float:
    yesterday = datetime.now().date() - timedelta(days=1)
    df = _filter_by_day(yesterday)
    if df.empty:
        return 0.0
    return float(df[df["tipo"] == "entrada"]["valor"].sum())


def list_recent_entries(limit: int = 5) -> list[dict]:
    df = _prepare_df()
    if df.empty:
        return []

    df["id_num"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.sort_values("id_num", ascending=False)

    recent = df.head(limit)
    results = []

    for _, row in recent.iterrows():
        results.append(
            {
                "id": row["id"],
                "data_evento": row["data_evento"].strftime("%Y-%m-%d"),
                "tipo": row["tipo"],
                "valor": float(row["valor"]),
                "categoria": row["categoria"],
                "descricao": row["descricao"],
            }
        )

    return results


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