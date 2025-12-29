# Relatório: Entendimento do Problema (RGM)

Este documento responde especificamente à **Parte 2** do case, definindo a estrutura estratégica e os KPIs do projeto.

---

## 1. Estrutura do Problema (Visão Revenue Growth Management)

Do ponto de vista de RGM, estruturamos este desafio dentro do pilar de **Eficiência Promocional** e **Pricing Tático**. O problema não é apenas "vender mais", mas "vender melhor".

A estrutura lógica adotada foi:

1.  **Diagnóstico de Elasticidade (O "Quem"):** Antes de decidir o desconto, precisamos entender a sensibilidade de cada SKU/Região. Descontos em produtos inelásticos destroem valor; descontos em elásticos geram volume.
2.  **Simulação de Cenários (O "E Se"):** Em vez de intuição, utilizamos simulação matemática para projetar o resultado financeiro de diferentes profundidades de desconto (0% a 30%).
3.  **Otimização de Alocação (O "Onde"):** A decisão final deve alocar o investimento (desconto) apenas onde o retorno financeiro (Lucro Incremental) for positivo, descendo ao nível granular de Loja/Região para evitar subsídios desnecessários.

---

## 2. Objetivos e Métricas de Negócio

### Objetivo Principal
**Maximizar o Lucro Incremental.**
Diferente de estratégias de "Market Share" puro, o foco da Americanas neste case (RGM) é crescimento rentável. A promoção só deve existir se a massa de lucro gerada for maior do que o lucro basal sem promoção.

### Métricas a Serem Maximizadas (KPIs Alvo)
1.  **Lucro Incremental (R$):**
    -   `Lucro Incremental = (Volume Promo * Margem Promo) - (Volume Base * Margem Base)`
    -   É a métrica "rainha". Se for negativo, a promoção não deve ocorrer.
2.  **ROI Promocional (%):**
    -   `ROI = Lucro Incremental / Investimento Promocional`
    -   Mede a eficiência de cada real "gasto" em desconto.

### Métricas a Serem Controladas (Guardrails)
1.  **Índice de Erosão de Preço (Price Erosion):**
    -   Devemos controlar o quanto o preço médio efetivo está caindo. Descontos muito frequentes "treinam" o cliente a só comprar na promoção, erodindo o valor da marca a longo prazo.
2.  **Canibalização (R$):**
    -   Venda perdida de produtos similares (ex: vender mais Samsung com desconto, mas derrubar a venda do Motorola margem cheia). Embora não tivéssemos dados profundos de substituição no case, é um controle vital em produção.
3.  **Risco de Ruptura (Stockout Risk):**
    -   Se a elasticidade for muito alta e o desconto agressivo, podemos zerar o estoque, gerando insatisfação e perda de venda futura. O volume projetado deve ser cruzado com o estoque disponível.
