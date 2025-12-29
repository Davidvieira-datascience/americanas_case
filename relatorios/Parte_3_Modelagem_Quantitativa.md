# Relatório: Modelagem Quantitativa (Parte 3)

Este documento detalha o modelo construído para simular cenários de preços e suportar a decisão de RGM.

---

## 1. Construção do Modelo Quantitativo

Para responder às perguntas de negócio ("O que acontece se eu baixar o preço?"), construímos um sistema em duas etapas:

### A. Modelo de Estimação de Elasticidade (Econométrico)
Utilizamos uma **Regressão Log-Log (Log-Linear)** para estimar a sensibilidade da demanda em relação ao preço.

**Equação do Modelo:**
$$ \ln(Vendas) = \alpha + \beta \cdot \ln(Preço) + \gamma \cdot \ln(PreçoConcorrente) + \epsilon $$

Onde:
*   $\beta$: Coeficiente de **Elasticidade-Preço Própria** (Ex: se $\beta = -2.0$, um aumento de 10% no preço reduz vendas em ~20%).
*   $\gamma$: Coeficiente de **Elasticidade Cruzada** (Impacto do concorrente).

### B. Simulador de Cenários
Com os coeficientes ($\beta$) calculados para cada par `Produto-Região`, criamos um motor de simulação determinística:

1.  Input: Descontos simulados (5%, 10%, ... 30%).
2.  Cálculo de Nova Demanda: $Q_{novo} = Q_{base} \cdot (P_{novo} / P_{base})^{\beta}$
3.  Cálculo Financeiro: Recalcula Receita, Custo e Lucro com o novo volume e novo preço.

---

## 2. Justificativas e Variáveis

### Por que este modelo?
1.  **Interpretabilidade:** O modelo Log-Log é o padrão ouro na indústria de varejo porque os coeficientes são diretamente as elasticidades. É fácil explicar para um Diretor Comercial.
2.  **Robustez:** Requer menos dados que redes neurais complexas ("Deep Learning") e funciona bem com dados tabulares ruidosos, pois foca na tendência média.

### Variáveis Utilizadas
| Tipo | Variável | Justificativa |
| :--- | :--- | :--- |
| **Alvo (Target)** | `ln(units_sold)` | O volume de vendas é o que queremos prever. Transformação Log suaviza a variância. |
| **Preditiva** | `ln(unit_price)` | O preço efetivo pago pelo cliente (pós-desconto). |
| **Preditiva** | `ln(competitor_price)` | O preço do concorrente mais relevante no dia (obtido via `ASOF join`). Define a atratividade relativa. |
| **Controle** | `product_id`, `region` | O modelo é treinado individualmente para cada combinação, garantindo especificidade local. |

---

## 3. Principais Limitações

Embora robusto, o modelo possui limitações que devem ser consideradas na produção:

1.  **Elasticidade Constante:** O modelo assume que a elasticidade é a mesma para qualquer faixa de preço. Na realidade, preços muito altos podem ter uma quebra estrutural de demanda (ninguém compra), e preços muito baixos podem saturar o mercado.
2.  **Sazonalidade e Eventos:** O modelo atual não isola explicitamente eventos como "Black Friday" ou "Natal". Se o preço cai na Black Friday, o modelo pode atribuir todo o aumento de volume ao preço, superestimando a elasticidade (viés).
    *   *Mitigação futura:* Adicionar variáveis dummy (`is_holiday`).
3.  **Ruptura de Estoque:** Se o histórico contém dias com venda zero por falta de estoque (e não por preço alto), o modelo pode aprender errado.
    *   *Mitigação:* Usamos filtros de limpeza, mas dados de estoque reais seriam ideais para censurar o modelo.
