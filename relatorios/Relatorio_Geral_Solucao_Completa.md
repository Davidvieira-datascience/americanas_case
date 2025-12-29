# Relatório Geral: Solução Completa do Case Americanas (RGM & Pricing)

**Autor:** [Seu Nome/Cargo]
**Data:** Dezembro/2025

Este relatório consolida minha solução integral para o desafio de Pricing e Revenue Growth Management, detalhando minha abordagem técnica, estratégica e de negócios para cada uma das 7 partes propostas.

---

## Parte 1: Engenharia & Preparação dos Dados (GCP)

### 1.1 Minha Estratégia de Ingestão no Google Cloud
Para garantir escalabilidade e governança, desenhei uma arquitetura **ELT (Extract, Load, Transform)** utilizando os serviços nativos do GCP.

*   **Ingestão (Extract/Load):**
    Eu optei por utilizar o **Cloud Storage** como *Landing Zone* para receber os arquivos CSV brutos (`sales`, `competitor`, `stores`).
    Desenvolvi o script Python `ingestion_gcp.py` que autentica via *Service Account* e carrega esses dados para a camada `raw_data` no **BigQuery**. Escolhi o BigQuery por sua capacidade de processar Petabytes sem necessidade de indexação manual.

*   **Transformações e Formato:**
    Dentro do BigQuery, estruturei as tabelas mantendo a granularidade original. Minha principal transformação foi na criação da **Tabela Mestra Analítica**.
    Eu utilizei a técnica de **`ASOF JOIN`** para cruzar as vendas com os preços dos concorrentes. Decidi por isso pois os dados de concorrentes não são diários; o `ASOF JOIN` me permitiu encontrar qual era o preço do concorrente "ativo" no exato momento de cada venda, evitando valores nulos que sujariam o modelo.

### 1.2 Minhas Decisões de Modelagem
Justifico minhas escolhas de design da seguinte forma:

1.  **Granularidade de Transação:** Mantive os dados nível item-nota fiscal. Eu decidi não agregar por mês/semana nesta etapa porque a elasticidade de preço ocorre no dia-a-dia. Se eu agregasse, perderia a nuance da reação do cliente a uma mudança pontual de preço.
2.  **Limpeza Rigorosa:** Identifiquei ruídos propositais na base (preços negativos). Implementei filtros no meu script `data_prep.py` para remover qualquer transação com `price <= 0` ou `cost <= 0`, pois esses dados distorceriam a regressão logarítmica.

---

## Parte 2: Entendimento do Problema (RGM)

### 2.1 Como Estruturei o Problema
Eu enquadrei este desafio sob a ótica de **Eficiência Promocional**. O problema central não é "como vender mais a qualquer custo", mas "como investir margem (desconto) apenas onde ela retorna lucro".

Minha estrutura lógica foi:
1.  **Diagnóstico:** Quem é sensível a preço? (Elasticidade).
2.  **Simulação:** O que acontece financeiramente se eu der 10%, 20% ou 30% de desconto?
3.  **Decisão:** Só aprovo o desconto se o Lucro Incremental for positivo.

### 2.2 Objetivos e KPIs que Defini
Defini como objetivo principal a **Maximização do Lucro Incremental**.
*   **Métrica Alvo (Maximizar):** Lucro Incremental ($$) e ROI Promocional (%).
*   **Métrica de Controle (Guardrail):** Índice de Canibalização e Erosão de Preço (Price Erosion). Eu estabeleci que não aceitaríamos queimar margem para ganhar *market share* neste momento, dado o perfil dos produtos.

---

## Parte 3: Modelagem Quantitativa

### 3.1 O Modelo que Construí
Para simular os cenários, eu desenvolvi um modelo econométrico de **Regressão Log-Log (Log-Linear)**.
A equação que utilizei foi:
$$ \ln(Demanda) = \alpha + \beta \cdot \ln(Preço) + \gamma \cdot \ln(PreçoConcorrente) $$

Com esse modelo, o coeficiente $\beta$ me dá diretamente a **Elasticidade-Preço**.

### 3.2 Por que escolhi este modelo e suas limitações
Eu escolhi o Log-Log pela **interpretabilidade**. É vital conseguir explicar para o Diretor Comercial que "um aumento de 10% no preço reduz 5% do volume" (Elasticidade -0.5), algo que "caixas pretas" de Deep Learning não entregam facilmente.

**Limitações que assumi:**
Reconheço que meu modelo assume elasticidade constante ao longo da curva de demanda, o que é uma simplificação. Além disso, o modelo atual não isola eventos de sazonalidade extrema (como Black Friday), podendo superestimar a elasticidade nesses períodos se não tratado.

---

## Parte 4: Elasticidade & Concorrência

### 4.1 Minhas Estimativas de Elasticidade
Ao rodar o modelo nos dados históricos (processo detalhado no script `eda_rgm.py`), encontrei um padrão claro: **Inelasticidade**.
Para a maioria dos produtos (ex: P2, P5, P8), minha estimativa de elasticidade ficou entre **-0.5 e +0.2**.
*   **Interpretação:** Meus dados mostram que o consumidor destes produtos não reage fortemente a variações de preço. Baixar o preço gera pouco volume extra.

### 4.2 Análise de Impacto da Concorrência
Investiguei a variável `competitor_price` no modelo para calcular a Elasticidade Cruzada.
**Minha Conclusão:** Não encontrei um concorrente com impacto estatisticamente relevante (positivo forte). Os coeficientes ficaram próximos de zero ou negativos. Isso me indicou que a nossa demanda é guiada mais por fatores internos (disponibilidade, marca) do que pelo preço do vizinho imediato.

---

## Parte 5: Minha Decisão de Pricing

### 5.1 Recomendação de Ação
Baseado nas 45 simulações que rodei (abrindo por Região e Produto), minha recomendação é: **NÃO REALIZAR PROMOÇÕES AGRESSIVAS.**

Em todos os cenários onde simulei descontos (5% a 30%), o resultado foi **Lucro Incremental Negativo**.
*   *Exemplo:* No Produto P1 (Norte), dar 20% de desconto geraria um prejuízo incremental de milhões, pois o volume subiria apenas ~2%.

### 5.2 Metodologia de Estimativa
Para chegar a essa conclusão, eu utilizei as seguintes fórmulas no script de otimização:
1.  **Lucro Incremental:** `(Volume_Novo * Margem_Nova) - (Volume_Base * Margem_Base)`.
2.  **Risco de Erosão:** Monitorei o preço médio efetivo. Como a demanda é inelástica, qualquer desconto vira "investimento a fundo perdido", erodindo o valor percebido da marca sem contrapartida.

---

## Parte 6: Comunicação Executiva

Preparei um sumário executivo focado na "Defesa de Margem".
Em minha comunicação para a diretoria, fui direto: mostrei que a "guerra de preços" seria ineficaz. Em vez de pedir verba para descontos, **propus um teste piloto de aumento de preços** (3% a 5%) em regiões específicas, projetando um ganho direto na última linha (Lucro Líquido) com risco mínimo de perda de volume.

---

## Parte 7: Produção & Escala

### 7.1 Pipeline MLOps Proposto
Se eu tivesse que implantar isso hoje em produção no GCP, minha arquitetura seria:
1.  **Orquestração:** **Cloud Composer (Airflow)** rodando DAGs diárias.
2.  **Processamento:** **dbt** no BigQuery para transformar os dados brutos na Tabela Mestra Analytic.
3.  **Inferência:** **Vertex AI** para gerenciar o ciclo de vida do modelo e servir as predições.

### 7.2 Monitoramento e Falhas
Desenhei uma estratégia de monitoramento focada em **Data Drift**.
*   **Onde vai falhar primeiro?** Identifiquei que a **Sazonalidade e Eventos (Feriados)** são o ponto fraco. Se não criarmos *features* de calendário ("is_black_friday"), o modelo vai errar feio nessas datas.
*   **Ação:** Configurei alertas no Vertex AI Model Monitoring para avisar se a distribuição de vendas fugir do padrão histórico de 30 dias.
