# Relatório: Produção & Escala (Parte 7)

Este documento responde especificamente à **Parte 7** do case, desenhando a arquitetura para produtização.

---

## 1. Pipeline de Produção no GCP (MLOps)

Se colocássemos este modelo em produção hoje, a arquitetura recomendada seria baseada em **Vertex AI** e **Cloud Composer (Airflow)**.

### A. O Pipeline (Workflow)
O fluxo seria orquestrado diariamente por uma DAG no Airflow:

1.  **Ingestão (Data Lake):**
    -   *Ferramenta:* Cloud Storage + BigQuery Transfer Service.
    -   *Ação:* Novos dados de venda (`D-1`) chegam no bucket e são ingeridos na `raw_sales`.
2.  **Preparação (Feature Store):**
    -   *Ferramenta:* dbt (Data Build Tool) rodando no BigQuery ou Dataflow.
    -   *Ação:* Limpeza, deduplicação e *ASOF Join* com concorrentes para criar a `master_table` do dia.
3.  **Inferência (Scoring):**
    -   *Ferramenta:* Vertex AI Batch Prediction.
    -   *Ação:* O modelo treinado (armazenado no Registry) recebe os dados do dia e cospe a previsão de demanda + recomendação de preço.
4.  **Consumo:**
    -   *Saída:* Tabela `recommendations_v1` no BigQuery, conectada a um dashboard no Looker/PowerBI para o time comercial aprovar.

### B. Monitoramento (Observabilidade)
Não basta rodar; precisamos saber se está funcionando.
-   **Data Drift (Verificação de Dados):**
    -   Monitorar se a distribuição dos preços mudou drasticamente (ex: concorrente baixou preço em 50% de repente). O *Vertex AI Model Monitoring* faz isso nativamente.
-   **Model Drift (Degradação de Performance):**
    -   Comparar `Previsão de Venda` vs `Venda Real` (`MAPE`). Se o erro subir acima de um limiar (ex: 20%), dispara alerta.

### C. Estratégia de Re-treinamento
-   **Gatilho:** Mensal (automático) OU Por Performance (se o monitoramento indicar degradação).
-   **Janela:** Treinar sempre com os últimos 12 meses (janela deslizante) para capturar tendências recentes sem esquecer a sazonalidade anual.

---

## 2. Onde o modelo tende a falhar primeiro?

Toda modelagem simplificada tem pontos cegos. Identificamos os críticos:

### A. Sazonalidade Extrema (O "Cisne Negro" do Varejo)
Esta é a falha mais provável.
-   **Cenário:** Na Black Friday, as vendas explodem não só pelo preço, mas pelo "evento".
-   **O Erro:** O modelo Log-Log simples vai achar que *todo* o aumento veio do preço baixo, calculando uma elasticidade artificialmente gigante.
-   **Consequência:** Em janeiro, o modelo recomendará descontos agressivos achando que vai vender muito, mas não vai (pois não é Black Friday).

### B. Ruptura de Estoque (Censura de Demanda)
-   **Cenário:** O produto acaba na prateleira. Venda = 0.
-   **O Erro:** O modelo vê "Preço = Padrão" e "Venda = 0". Ele "aprende" que o preço atual mata a venda.
-   **Consequência:** Recomenda baixar o preço desnecessariamente, quando o problema era logístico.

### C. Reação da Concorrência (Guerra de Preços)
-   **O Erro:** O modelo assume que o concorrente é estático (usa o preço de d-1). Se iniciarmos uma guerra de preços, a elasticidade muda dinamicamente, invalidando os parâmetros históricos.
