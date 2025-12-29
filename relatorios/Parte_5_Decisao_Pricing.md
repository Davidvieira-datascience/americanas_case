# Relatório de Decisão de Pricing e Otimização

## Objetivo do Modelo
Maximizar o **Lucro Incremental** e o **ROI Promocional**, respondendo:
1.  Quais produtos promover?
2.  Qual desconto aplicar?
3.  Em quais regiões?

## Resumo da Decisão Estratégica
> [!CRITICAL]
> **DECISÃO: NÃO APLICAR DESCONTOS (Manutenção de Preço Base)**

O modelo matemático de otimização rodou simulando 45 cenários granularizados por Região e Produto. **Nenhum cenário de desconto resultou em ROI positivo.**

### Por que esta decisão foi tomada?
A elasticidade-preço da demanda identificada atual é **inelástica** (|E| < 1) para a maioria dos SKUs principais.
-   **Significado Econômico:** O consumidor não reage fortemente à baixa de preço. O aumento de volume venda (+Vendas) não é suficiente para cobrir a perda de margem unitária (-Margem).
-   **Impacto Financeiro:** Qualquer real dado de desconto reduz o Lucro Líquido diretamente.

---

## Detalhamento dos Resultados da Simulação

Abaixo, exemplos reais extraídos da nossa simulação mostrando a destruição de valor ao tentar promover:

| Produto | Região | Desconto Simulado | Variação de Venda (Volume) | Prejuízo Gerado (Lucro Incremental) | ROI da Campanha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | Norte | 20% (OFF) | + ~2% (Est.) | **- R$ 2.589.167** | **Negativo (-102%)** |
| **P5** | Sudeste | 10% (OFF) | + ~1.5% (Est.) | **- R$ 850.400** | **Negativo** |
| **P8** | Sul | 30% (OFF) | + ~4% (Est.) | **- R$ 1.200.000** | **Negativo** |

*Nota: Valores baseados no modelo de elasticidade log-linear treinado com dados históricos.*

### Análise Regional
O comportamento se manteve consistente entre as regiões (Norte, Sul, Sudeste, etc.). Não identificamos "bolsões de oportunidade" onde a sensibilidade a preço fosse alta o suficiente para justificar uma campanha regionalizada.

---

## 2. Metodologia: Como estimamos os Resultados?

Respondendo à questão metodológica *"Como você estima lucro incremental, ROI e riscos?"*:

### A. Lucro Incremental (A métrica de decisão)
Não olhamos apenas para a Receita. Calculamos o lucro extra gerado *apenas* pela promoção:
$$ \Delta Lucro = (Vol_{promo} \times Margem_{promo}) - (Vol_{base} \times Margem_{base}) $$
*Onde $Vol_{promo}$ é a demanda prevista pela elasticidade ($Q_1 = Q_0 \times (P_1/P_0)^\beta$).*

### B. ROI Promocional
Mede o retorno sobre o investimento feito em desconto:
$$ ROI = \frac{\text{Lucro Incremental}}{\text{Investimento}} $$
*Investimento = $(Preço_{base} - Preço_{promo}) \times Vol_{promo}$*
(Se o Lucro Incremental for negativo, o ROI é negativo, indicando destruição de valor).

### C. Risco de Erosão de Preço
Monitoramos a variação entre o Preço de Tabela e o Preço Praticado Médio Ponderado.
-   **No Modelo:** Calculamos o novo "Preço Médio Efetivo" após o mix de vendas promocionais. Se este preço cair > 10% sem ganho de massa de margem, sinalizamos alerta vermelho de erosão.

---

## 3. Recomendação Final de Ação
1.  **Imediato:** Manter tabela de preços atual. Focar em disponibilidade (evitar ruptura) e nível de serviço.
2.  **Teste A/B de Aumento:** Dado que a demanda é inelástica, recomenda-se testar um **aumento de preço de 3% a 5%** no Produto P1 (Região Norte) em ambiente controlado. O modelo prevê que o volume cairá muito pouco, gerando aumento direto de Lucro.
3.  **Investigação de Dados:** A inelasticidade forte pode ser sinal de fidelidade à marca ou falta de concorrentes diretos relevantes na percepção do shopper.

---
**Status do Pipeline:**
-   Dados carregados no GCP (`raw_data`).
-   Modelos salvos e prontos para re-treino mensal.
