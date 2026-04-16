from __future__ import annotations

import re
from datetime import datetime, timedelta
from dateutil.parser import parse as date_parse

from categories import infer_category


EXPENSE_HINTS = ["gastei", "paguei", "comprei"]
INCOME_HINTS = ["recebi", "entrou", "ganhei", "salario", "salário"]


def detect_intent(text: str) -> str:
    lowered = text.lower().strip()

    # CONSULTAS primeiro
    if "resumo" in lowered:
        return "gerar_resumo_mes"

    if "saldo" in lowered:
        return "consultar_saldo_mes"

    if "quanto gastei com" in lowered or "quanto foi" in lowered:
        return "consultar_categoria_mes"

    if "quanto gastei" in lowered:
        return "consultar_total_mes"

    # REGISTROS depois
    if any(word in lowered for word in EXPENSE_HINTS):
        return "registrar_despesa"

    if any(word in lowered for word in INCOME_HINTS):
        return "registrar_receita"

    # fallback inteligente
    has_number = re.search(r"\d+", lowered)
    if has_number:
        if any(word in lowered for word in ["salario", "salário"]):
            return "registrar_receita"
        return "registrar_despesa"

    return "desconhecido"


def extract_value(text: str) -> float | None:
    match = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not match:
        return None

    raw = match.group(1).strip()

    if "," in raw:
        return float(raw.replace(".", "").replace(",", "."))

    return float(raw)


def extract_payment_method(text: str) -> str:
    lowered = text.lower()

    if "pix" in lowered:
        return "pix"

    if "cartao" in lowered or "cartão" in lowered:
        return "cartao"

    if "dinheiro" in lowered:
        return "dinheiro"

    if "debito" in lowered or "débito" in lowered:
        return "debito"

    if "credito" in lowered or "crédito" in lowered:
        return "credito"

    return ""


def extract_date(text: str) -> str:
    lowered = text.lower()
    today = datetime.now().date()

    if "ontem" in lowered:
        return str(today - timedelta(days=1))

    if "hoje" in lowered:
        return str(today)

    # Só tenta parsear data se houver padrão real de data
    has_explicit_date = (
        re.search(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", lowered) or
        re.search(r"\b\d{1,2}-\d{1,2}(?:-\d{2,4})?\b", lowered)
    )

    if has_explicit_date:
        try:
            parsed = date_parse(text, fuzzy=True, dayfirst=True)
            return str(parsed.date())
        except Exception:
            return str(today)

    return str(today)


def extract_description(text: str) -> str:
    lowered = text.lower()

    noise = [
        "gastei",
        "paguei",
        "comprei",
        "recebi",
        "entrou",
        "ganhei",
        "salario",
        "salário",
        "no",
        "na",
        "com",
        "de",
        "do",
        "da",
        "ontem",
        "hoje",
        "pix",
        "cartao",
        "cartão",
        "dinheiro",
        "debito",
        "débito",
        "credito",
        "crédito",
    ]

    cleaned = re.sub(r"(\d+(?:[.,]\d+)?)", "", lowered)

    for token in noise:
        cleaned = re.sub(rf"\b{token}\b", "", cleaned)

    cleaned = " ".join(cleaned.split())
    return cleaned.strip() or "sem descricao"


def parse_financial_message(text: str) -> dict:
    intent = detect_intent(text)

    if intent not in {"registrar_despesa", "registrar_receita"}:
        return {"intent": intent}

    entry_type = "saida" if intent == "registrar_despesa" else "entrada"
    value = extract_value(text)
    payment_method = extract_payment_method(text)
    event_date = extract_date(text)
    description = extract_description(text)
    category = infer_category(text, entry_type)

    return {
        "intent": intent,
        "tipo": entry_type,
        "valor": value,
        "categoria": category,
        "descricao": description,
        "forma_pagamento": payment_method,
        "data_evento": event_date,
    }