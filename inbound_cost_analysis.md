
# Análise de Custos de Envio: Full (Inbound)

Com base nos dados fornecidos (Screenshots), realizamos uma análise da correlação entre **Quantidade Enviada** e **Custo Unitário**.

## Dados Extraídos

| Envio | Qtd | Custo Total (R$) | Custo/Unid (R$) | Status |
| :--- | :---: | :---: | :---: | :--- |
| #49082871 | 4 | 74.35 | **18.58** | 🚨 Crítico |
| #44066867 | 6 | 87.94 | **14.65** | 🚨 Crítico |
| #48637308 | 8 | 82.94 | **10.36** | 🚨 Crítico |
| #45137103 | 20 | 98.10 | **4.90** | ⚠️ Alto |
| #49229207 | 16 | 71.07 | **4.44** | ⚠️ Alto |
| #49741241 | 24 | 83.06 | **3.46** | ⚠️ Alto |
| #46239775 | 30 | 99.68 | **3.32** | ⚠️ Alto |
| #48438183 | 21 | 67.50 | **3.21** | ⚠️ Alto |
| #41694936 | 21 | 64.88 | **3.09** | ⚠️ Alto |
| #49818795 | 40 | 100.98 | **2.52** | 🔸 Médio |
| #39072470 | 34 | 66.05 | **1.94** | 🔸 Médio |
| #40316064 | 61 | 85.25 | **1.39** | ✅ Bom |
| #42562303 | 80 | 109.96 | **1.37** | ✅ Bom |
| #49082872 | 69 | 85.07 | **1.23** | ✅ Bom |
| #49741267 | 65 | 72.96 | **1.12** | ✅ Bom |
| #43872289 | 53 | 57.66 | **1.08** | ✅ Bom |
| #48228658 | 67 | 70.86 | **1.05** | ✅ Bom |
| #37276764 | 95 | 99.37 | **1.04** | ✅ Bom |
| #37745886 | 154 | 143.16 | **0.93** | 💎 Ótimo |
| #47319326 | 94 | 76.14 | **0.81** | 💎 Ótimo |
| #40530445 | 244 | 198.07 | **0.81** | 💎 Ótimo |
| #43299061 | 112 | 88.90 | **0.79** | 💎 Ótimo |
| #40290259 | 83 | 61.78 | **0.74** | 💎 Ótimo (Performance Excepcional para qtd média) |
| #47093959 | 78 | 57.68 | **0.74** | 💎 Ótimo |
| #46645538 | 96 | 66.75 | **0.69** | 💎 Ótimo |
| #48638086 | 102 | 59.00 | **0.58** | 🚀 Melhor Caso |
| #38283039 | 111 | 62.53 | **0.56** | 🚀 Melhor Caso |

## Conclusões

1.  **Custo Fixo Oculto**: Existe um custo base para mobilizar um envio (coleta/transportadora) que torna envios pequenos inviáveis. Enviar menos de 10 unidades custa **~R$ 15,00/unidade**, destruindo qualquer margem.
2.  **Zona de Perigo (< 40 un)**: Envios entre 20-40 unidades ainda custam caro (~R$ 3,00 - R$ 4,00).
3.  **Ponto de Virada (60-80 un)**: A partir de 60 unidades, o custo cai para **~R$ 1,20**, tornando-se aceitável.
4.  **Zona de Eficiência (100+ un)**: Acima de 100 unidades, o custo estabiliza na faixa de **R$ 0,60 a R$ 0,80**.

## Recomendação Estratégica

*   **Regra de Ouro**: Nunca agendar envios com menos de **80 unidades** (idealmente 100+).
*   **Acumular para Economizar**: É melhor esperar 3 dias e enviar 150 itens de uma vez do que fazer 3 envios de 50 itens. A economia estimada é de **R$ 1,50 por peça**, o que em 150 peças representa **R$ 225,00 de lucro puro** salvo apenas por logística eficiente.
*   **Valor para Configuração**: Recomendo atualizar a configuração global `avg_inbound_cost` para **R$ 0,85** (média conservadora para envios otimizados).
