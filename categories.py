CATEGORY_RULES = {
    "alimentacao": ["almoço", "almoco", "mercado", "padaria", "lanche", "café", "cafe", "janta"],
    "transporte": ["uber", "gasolina", "onibus", "ônibus", "taxi", "táxi"],
    "moradia": ["aluguel", "condominio", "condomínio"],
    "contas": ["energia", "agua", "água", "internet", "luz", "telefone"],
    "saude": ["farmacia", "farmácia", "remedio", "remédio", "consulta"],
    "lazer": ["cinema", "bar", "passeio", "show"],
    "assinaturas": ["netflix", "spotify", "prime", "disney"],
    "compras": ["roupa", "tenis", "tênis", "eletronico", "eletrônico"],
    "educacao": ["curso", "faculdade", "livro"],
    "investimentos": ["investimento", "aplicacao", "aplicação"],
    "presentes": ["presente"],
    "taxas": ["juros", "tarifa", "multa"],
}

DEFAULT_INCOME_CATEGORY = "trabalho"
DEFAULT_EXPENSE_CATEGORY = "outros"


def infer_category(text: str, entry_type: str) -> str:
    lowered = text.lower()

    if entry_type == "entrada":
        if "salario" in lowered or "salário" in lowered or "freela" in lowered or "freelance" in lowered:
            return "trabalho"
        return DEFAULT_INCOME_CATEGORY

    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in lowered for keyword in keywords):
            return category

    return DEFAULT_EXPENSE_CATEGORY