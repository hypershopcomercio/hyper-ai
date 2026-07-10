# Painel de fluxo de caixa e margem

O painel `GET /api/financial/cashflow-panel?days=30` é somente leitura. Ele deixa explícito que a margem operacional e o serviço da dívida são indicadores diferentes:

- margem operacional = contribuição das vendas - Ads reais - custos operacionais;
- caixa = recebimentos projetados - vencimentos operacionais - compras abertas - parcelas;
- parcelas não entram na margem operacional, mas aparecem no fluxo exatamente no dia de vencimento.

Não há migration. A categoria já existente em `financial_costs` recebe o valor `debt_service` para classificar uma parcela como obrigação de caixa.

## SQL manual (DBeaver)

Rode e valide cada etapa separadamente. Ajuste somente os IDs/nomes que correspondem ao seu cadastro.

```sql
SELECT id, name, amount, category, day_of_month, active
FROM financial_costs
WHERE active = 1
ORDER BY day_of_month, name;
```

```sql
UPDATE financial_costs
SET category = 'debt_service'
WHERE id IN (/* IDs de BAK, capital de giro, DIFAL e DAS parcelados */);
```

```sql
SELECT id, name, amount, category, day_of_month
FROM financial_costs
WHERE category = 'debt_service'
  AND active = 1
ORDER BY day_of_month, name;
```

Se uma parcela ainda não existir, cadastre-a em **Financeiro → Custos Fixos** escolhendo **Serviço da dívida / Parcelas**. O painel não grava nem modifica contas.
