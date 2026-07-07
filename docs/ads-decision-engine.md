# Motor de Decisão de Ads — Design

> Status: DESENHO APROVAÇÃO PENDENTE · Criado em 2026-07-06
> Princípio inegociável (regras do projeto): nenhuma escrita no ML sem flag explícita.
> `ADS_WRITE_ENABLED = false` por padrão, sempre.

## 1. Escada de autonomia

O sistema evolui por níveis. Cada nível só é ativado após o anterior rodar
estável e com validação humana dos resultados.

| Nível | Nome | O que faz | Escrita no ML? | Status |
|-------|------|-----------|----------------|--------|
| 0 | Diagnóstico | Classifica cada anúncio e sugere ação com justificativa e impacto | Não | **PRONTO** (endpoint + página Ads Intelligence) |
| 1 | Fila de recomendações | Persiste recomendações com estado (pendente/aceita/rejeitada/expirada); usuário aceita com 1 clique; sistema executa a ação aceita e audita | Sim, mediante clique humano | Próximo |
| 2 | Auto-pilot com guardrails | Executa sozinho APENAS ações de baixo risco e alta confiança, dentro de limites diários; relatório do que fez | Sim, restrita | Depois do 1 |
| 3 | Otimização de portfólio | Realoca verba entre anúncios/campanhas pelo lucro marginal (tirar de quem queima, dar a quem escala) | Sim | Visão de longo prazo |

## 2. Variáveis do modelo de decisão

1. **Margem real do produto** (PricingDataResolver / NF-e / Tiny) — é o TETO absoluto de ACOS.
   Sem margem cadastrada → decisões só conservadoras (nunca escalar às cegas).
2. **Ciclo de vida do anúncio** — o ACOS aceitável muda por fase:
   - `lancamento` (primeiros ~21 dias de Ads OU < 30 vendas via Ads): tolera ACOS até ~100% da margem
     (compra de ranking/velocidade; prejuízo zero, não lucro).
   - `crescimento`: ACOS-alvo ≤ 70% da margem.
   - `maturidade`: ACOS-alvo ≤ 40–60% da margem (Ads é acelerador, não muleta).
   - `liquidacao` (estoque encalhado): tolera ACOS alto — capital parado também custa.
   - Fase inferida automaticamente (idade do anúncio, vendas acumuladas, dias de estoque),
     com override manual por item.
3. **Estoque (forecast existente)**:
   - dias_de_estoque < lead time de reposição → NUNCA escalar (vender rápido o que vai faltar é queimar ranking à toa);
   - estoque > X dias de cobertura → candidato a acelerar Ads.
4. **Significância estatística** — mínimo de evidência antes de agir:
   ≥ 30 cliques OU ≥ R$ (2× ticket médio de CPC×30) gastos no período. Amostra pequena → "aguardar dados".
5. **Share orgânico (TACOS)** — se o item vende bem organicamente e o TACOS é baixo,
   reduzir Ads pode não derrubar vendas (testar com redução gradual, nunca corte seco).
6. **Tendência** — comparar janela 7d vs 30d: ACOS piorando 3 dias seguidos antecipa ação.
7. **Custo de oportunidade** — verba é finita: ranking de anúncios por lucro marginal por real investido.

## 3. Ações do catálogo (o que o sistema pode decidir)

| Código | Ação | Risco | Auto no nível 2? |
|--------|------|-------|------------------|
| `pausar` | Pausar anúncio na campanha | Baixo (reversível) | Sim, com guardrails |
| `reduzir_ou_pausar` | Reduzir exposição/lance ou pausar | Médio | Não (sugestão) |
| `aumentar` | Aumentar verba/prioridade do item | Médio | Não (sugestão) |
| `adicionar_campanha` | Adicionar item sem Ads a uma campanha | Médio | Não |
| `mover_campanha` | Mover item entre campanhas (ACOS-alvo diferente) | Médio | Não |
| `ajustar_budget` | Mudar budget diário da campanha | Alto | Nunca |
| `manter` / `aguardar_dados` | Nada a fazer / amostra insuficiente | — | — |

Guardrails do nível 2 (todos configuráveis):
- Máx. N ações automáticas/dia (começar com 3).
- Só `pausar` com: gasto ≥ R$30 no período E 0 vendas via Ads E ≥ 30 cliques E fora da fase `lancamento`.
- Kill-switch global (`ADS_WRITE_ENABLED`) + log completo + reversível com 1 clique.
- Toda ação automática notificada no mesmo dia.

## 4. Infraestrutura necessária (Fase B — próxima)

- Tabela `ads_recommendations`: id, item_id, action_code, reason, metrics_snapshot (JSON),
  status (pending/accepted/rejected/expired/executed), created_at, decided_at, decided_by,
  executed_at, execution_result, outcome_measured_at, outcome (JSON).
- Job diário (após sync das 04:00): recalcula classificações → gera recomendações novas
  (sem duplicar pendentes do mesmo item+ação) → expira as obsoletas.
- **Feedback loop**: 7/14 dias após execução, medir o resultado real (lucro, vendas, ACOS)
  vs. snapshot — é o que permite calibrar thresholds com dados próprios.
- Validar endpoints de ESCRITA da API Product Ads v2 (pausar ad, mover, budget) — mesma
  família dos de leitura já integrados (Api-Version 2, advertiser 347940).

## 5. Decisões que precisam do usuário (ATENÇÃO)

1. Thresholds iniciais das fases de ciclo de vida (21 dias? 30 vendas?) — chutes educados, calibrar depois.
2. Quando ativar o nível 1 (fila com execução por clique) — exige habilitar escrita no ML.
3. Orçamento total de Ads é gerido pelo usuário ou o sistema pode sugerir realocação entre campanhas?
4. Canal de notificação das recomendações (só a página? e-mail? WhatsApp?).
