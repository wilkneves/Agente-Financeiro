from __future__ import annotations

from datetime import datetime

from parser import parse_financial_message, detect_intent
from queries import (
    balance_month,
    monthly_summary,
    total_by_category_month,
    total_expenses_month,
)
from storage import append_entry, ensure_storage, next_id


def brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def save_financial_entry(message: str) -> str:
    parsed = parse_financial_message(message)

    if parsed.get("valor") is None:
        return "Não entendi o valor. Pode me dizer quanto foi?"

    entry = {
        "id": next_id(),
        "data_evento": parsed["data_evento"],
        "data_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": parsed["tipo"],
        "valor": parsed["valor"],
        "categoria": parsed["categoria"],
        "descricao": parsed["descricao"],
        "forma_pagamento": parsed["forma_pagamento"],
        "observacoes": "",
        "mensagem_original": message,
    }

    append_entry(entry)

    if parsed["tipo"] == "saida":
        return f"Registrei {brl(parsed['valor'])} em {parsed['categoria']}."
    return f"Entrada registrada: {brl(parsed['valor'])} em {parsed['categoria']}."


def handle_query(message: str) -> str:
    lowered = message.lower().strip()

    if "quanto gastei com" in lowered:
        category = lowered.split("quanto gastei com")[-1]
        category = category.replace("este mês", "").replace("esse mês", "").strip()
        total = total_by_category_month(category)
        return f"Você gastou {brl(total)} com {category} neste mês."

    if "quanto foi" in lowered:
        category = lowered.split("quanto foi")[-1]
        category = category.replace("com", "").replace("este mês", "").replace("esse mês", "").strip()
        total = total_by_category_month(category)
        return f"Você gastou {brl(total)} com {category} neste mês."

    if "quanto gastei" in lowered:
        total = total_expenses_month()
        return f"Você gastou {brl(total)} neste mês."

    if "saldo" in lowered:
        total = balance_month()
        return f"Seu saldo no mês está em {brl(total)}."

    if "resumo" in lowered:
        summary = monthly_summary()
        return (
            f"Resumo do mês: entraram {brl(summary['entradas'])}, "
            f"saíram {brl(summary['saidas'])} e o saldo está em {brl(summary['saldo'])}. "
            f"Sua maior categoria foi {summary['maior_categoria']}."
        )

    return "Não entendi esse pedido ainda."


def main() -> None:
    ensure_storage()
    print("Agente financeiro iniciado. Digite 'sair' para encerrar.")

    while True:
        message = input("\nVocê: ").strip()

        if message.lower() == "sair":
            print("Encerrado.")
            break

        intent = detect_intent(message)

        if intent in {"registrar_despesa", "registrar_receita"}:
            response = save_financial_entry(message)
        else:
            response = handle_query(message)

        print(f"Agente: {response}")


if __name__ == "__main__":
    main()