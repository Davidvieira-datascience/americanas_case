# Relatório: Engenharia & Preparação dos Dados (GCP)

Este documento responde especificamente à **Parte 1** do case, detalhando a estratégia de ingestão e modelagem adotada.

---

## 1. Ingestão de Dados no Google Cloud Platform (BigQuery)

### Estratégia de Arquitetura
Utilizamos uma arquitetura **ELT (Extract, Load, Transform)** moderna, focada em agilidade e escalabilidade no BigQuery.

1.  **Landing Zone (Cloud Storage):**
    -   Os arquivos CSV brutos (`sales_history.csv`, `competitor_prices.csv`, `stores.csv`) são enviados para um bucket no GCS (ex: `gs://americanas-datalake/raw/`).
    -   *Motivo:* Desacopla o armazenamento do processamento e serve como backup imutável.

2.  **Camada Raw (BigQuery):**
    -   Criamos tabelas no dataset `raw_data` que espelham exatamente os CSVs.
    -   *Ingestão:* Script Python (`scripts/ingestion_gcp.py`) utilizando a biblioteca oficial `google-cloud-bigquery`.
    -   *Método:* Carga em Batch (Job `LoadJobConfig`) com `WRITE_TRUNCATE` para cargas full ou `WRITE_APPEND` para incrementais.

### Estrutura das Tabelas & Formato
| Tabela | Formato de Origem | Particionamento Sugerido | Schema |
| :--- | :--- | :--- | :--- |
| `raw_sales_history` | CSV | Por Data (`date_order`) | Híbrido (String p/ IDs, Float p/ valores). |
| `raw_competitor_prices` | CSV | Por Data (`datetime_extraction`) | Clusterização por `product_id` (para agilizar queries de comparação). |
| `raw_stores` | CSV | N/A (Tabela Pequena) | Dimensão simples. |

### Transformações Necessárias (Pipeline)
As transformações ocorrem via SQL/Pandas após a carga na Raw:
-   **Tipagem Forte:** Conversão de strings de data (`YYYY-MM-DD`) para tipo `DATE` nativo.
-   **Sanitização:** Remoção de caracteres especiais e espaços em chaves.

---

## 2. Decisões de Modelagem de Dados

Para viabilizar a análise de RGM e Elasticidade, construímos uma **Tabela Mestra Analítica** (`master_table`). Abaixo as principais decisões e seus "porquês".

### A. Granularidade: Transação (Item a Item)
-   **Decisão:** Manter a análise no nível de cada venda (`sale_id` + `product_id`), em vez de agregar mensalmente logo de início.
-   **Por quê?** Elasticidade é sensível. Precisamos saber se o cliente pagou R$ 100,00 ou R$ 90,00 **naquele dia específico**. Agregar pela média mensal suavizaria variações de preço e esconderia o comportamento real de resposta do consumidor.

### B. Tratamento Temporal de Concorrentes (`ASOF Join`)
-   **Decisão:** Cruzar vendas com preços de concorrentes usando lógica "As Of" (o preço do concorrente válido no momento da venda, ou o mais recente anterior).
-   **Por quê?** Tabelas de concorrentes têm datas de extração esparsas (não diárias para tudo). Um `Left Join` simples por data geraria muitos nulos. O `ASOF` garante que sempre temos o "preço de referência" mais atual que o cliente poderia ter visto.

### C. Limpeza de Ruídos de Negócio
-   **Decisão:** Excluir vendas com `price <= 0` ou `cost <= 0`.
-   **Por quê?** no contexto do case, foi avisado que havia dados ruidosos. Preço zero pode ser erro de sistema, bonificação ou troca, não refletindo uma decisão de compra baseada em preço (elasticidade), o que sujaria o modelo.

### D. Enriquecimento Regional
-   **Decisão:** Desnormalizar dados de Loja (`region`, `cluster`) para a tabela de fatos.
-   **Por quê?** Para permitir o cálculo de elasticidade por Região (como demonstrado no relatório de decisão). O comportamento de preço no Nordeste pode ser diferente do Sul, e a tabela mestra unificada facilita essa quebra dinâmica.
