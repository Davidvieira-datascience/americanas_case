# Relatório: Elasticidade & Concorrência (Parte 4)

Este documento responde especificamente à **Parte 4** do case.

---

## 1. Estimativa de Elasticidades de Preço

Realizamos o cálculo estatístico da Elasticidade-Preço da Demanda (PED) com granularidade de **Produto x Região**.

**Metodologia:**
Regressão Log-Log treinada em dados históricos (transações individuais), controlando pelo preço do concorrente.

**Resultados Encontrados:**
A grande maioria dos SKUs analisados apresentou comportamento **Inelástico** (Elasticidade > -1) e, em muitos casos, **Positiva**.

| Produto Exemplo | Região | Elasticidade Própria ($\beta$) | Interpretação |
| :--- | :--- | :--- | :--- |
| **P4** | Nordeste | **+0.07** | **Altamente Inelástico.** Variações de preço praticamente não afetam o volume (ou vendas sobem levemente com preço, indicando anomalia ou valor percebido). |
| **P2** | Sul | **+0.10** | **Inelástico.** Reduzir preço não gera volume suficiente. |
| **P8** | Sudeste | **+0.20** | **Inelástico.** Candidato a aumento de preço para captura de margem. |

> **Conclusão de Negócio:** A base de clientes atual, para estes produtos e regiões, não é sensível a desconto. Promoções destruiriam valor.

---

## 2. Análise de Concorrência

### Existe algum concorrente com impacto relevante?
**Resposta:** Para os produtos analisados (Top Sellers), **NÃO** identificamos, estatisticamente, um concorrente com impacto substitutivo forte e consistente (Elasticidade Cruzada Positiva alta).

### Como identificamos isso?
Utilizamos a **Elasticidade Cruzada de Preços (Cross-Price Elasticity)** no modelo de regressão.

-   **Coeficiente Analisado ($\gamma$):** Mede a variação na *nossa* venda dado a variação no *preço deles*.
-   **Esperado para Concorrentes Fortes:** Valor Positivo alto (Eles sobem o preço -> Clientes vêm para nós).
-   **Observado:**
    -   Muitos valores próximos de zero ou negativos (ex: P4 Nordeste = -0.04).
    -   Valores negativos indicam comportamento de bens complementares ou independência, mas *nunca* substituição direta feroz.

**Implicações:**
1.  **Independência de Pricing:** Temos espaço para manobrar preços sem temer retaliação imediata ou migração massiva de clientes para o concorrente monitorado.
2.  **Foco Interno:** O maior driver de rentabilidade agora é nossa própria eficiência de margem, não o "ataque" ao share do vizinho.
