from __future__ import annotations

from datetime import datetime

from parser import (
    detect_intent,
    parse_delete_request,
    parse_edit_request,
    parse_financial_message,
)
from queries import (
    balance_month,
    list_recent_entries,
    monthly_summary,
    total_by_category_month,
    total_expenses_month,
    total_expenses_today,
    total_expenses_yesterday,
    total_income_month,
    total_income_today,
    total_income_yesterday,
)
from storage import (
    append_entry,
    delete_entry_by_description,
    delete_last_entry,
    ensure_storage,
    next_id,
    update_entry_category_by_description,
    update_entry_value_by_description,
)


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


def handle_delete(message: str) -> str:
    parsed = parse_delete_request(message)

    if parsed["tipo_exclusao"] == "ultimo":
        removed = delete_last_entry()
        if not removed:
            return "Não encontrei lançamentos para apagar."
        return (
            f"Apaguei o último lançamento: {brl(float(removed['valor']))} "
            f"em {removed['categoria']} ({removed['descricao']})."
        )

    removed = delete_entry_by_description(parsed["alvo"])
    if not removed:
        return f"Não encontrei lançamento com '{parsed['alvo']}'."

    return (
        f"Apaguei o lançamento: {brl(float(removed['valor']))} "
        f"em {removed['categoria']} ({removed['descricao']})."
    )


def handle_edit(message: str) -> str:
    parsed = parse_edit_request(message)

    if parsed["tipo_correcao"] == "valor":
        updated = update_entry_value_by_description(parsed["alvo"], parsed["novo_valor"])
        if not updated:
            return f"Não encontrei lançamento com '{parsed['alvo']}'."

        return (
            f"Atualizei o valor de {updated['descricao']} para "
            f"{brl(float(updated['valor']))}."
        )

    if parsed["tipo_correcao"] == "categoria":
        updated = update_entry_category_by_description(parsed["alvo"], parsed["nova_categoria"])
        if not updated:
            return f"Não encontrei lançamento com '{parsed['alvo']}'."

        return (
            f"Atualizei a categoria de {updated['descricao']} para "
            f"{updated['categoria']}."
        )

    return "Não entendi a correção. Exemplo: corrige o almoço para 40"


def handle_recent_entries() -> str:
    entries = list_recent_entries(limit=5)

    if not entries:
        return "Você ainda não tem lançamentos."

    lines = ["Seus últimos lançamentos:"]
    for entry in entries:
        sinal = "-" if entry["tipo"] == "saida" else "+"
        lines.append(
            f"{entry['data_evento']} | {sinal}{brl(entry['valor'])} | "
            f"{entry['categoria']} | {entry['descricao']}"
        )

    return "\n".join(lines)


def handle_query(message: str) -> str:
    lowered = message.lower().strip()

    if detect_intent(message) == "listar_ultimos_lancamentos":
        return handle_recent_entries()

    if detect_intent(message) == "consultar_gastos_hoje":
        total = total_expenses_today()
        return f"Hoje você gastou {brl(total)}."

    if detect_intent(message) == "consultar_gastos_ontem":
        total = total_expenses_yesterday()
        return f"Ontem você gastou {brl(total)}."

    if detect_intent(message) == "consultar_receitas_hoje":
        total = total_income_today()
        return f"Hoje você recebeu {brl(total)}."

    if detect_intent(message) == "consultar_receitas_ontem":
        total = total_income_yesterday()
        return f"Ontem você recebeu {brl(total)}."

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

    if "quanto recebi" in lowered:
        total = total_income_month()
        return f"Você recebeu {brl(total)} neste mês."

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
        elif intent in {"apagar_ultimo", "apagar_por_descricao"}:
            response = handle_delete(message)
        elif intent == "corrigir_lancamento":
            response = handle_edit(message)
        else:
            response = handle_query(message)

        print(f"Agente: {response}")


if __name__ == "__main__":
    main()