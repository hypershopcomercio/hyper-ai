"""Classifica contas recorrentes sem alterar o schema financeiro existente."""

# Estas categorias representam compromissos de caixa/serviço da dívida. Elas não
# participam da margem operacional: uma empresa pode ter operação saudável e,
# ainda assim, caixa pressionado por parcelas.
DEBT_SERVICE_CATEGORIES = frozenset({
    "debt_service",
    "loan",
    "financing",
    "installment",
    "tax_installment",
})


def is_debt_service(category: str | None) -> bool:
    """Retorna se a categoria deve aparecer como obrigação de caixa."""
    return (category or "").strip().lower() in DEBT_SERVICE_CATEGORIES
