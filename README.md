# Americanas Case: Pricing Strategy & RGM

Solução completa para o desafio de Pricing e Revenue Growth Management (RGM), focada em maximização de lucro incremental e eficiência promocional.

## 📁 Estrutura do Projeto

*   **`scripts/`**: Códigos Python para automação e análise.
    *   `ingestion_gcp.py`: Ingestão de dados no BigQuery (Simulado/Real).
    *   `data_prep.py`: Limpeza e engenharia de features.
    *   `eda_rgm.py`: Análise exploratória e cálculo de elasticidade.
    *   `optimization.py`: Motor de simulação de cenários e decisão de pricing.
*   **`relatorios/`**: Documentação detalhada da solução (Partes 1 a 7).
    *   `Relatorio_Geral_Solucao_Completa.md`: Visão unificada de toda a estratégia.

## 🚀 Como Rodar

1.  **Instalar dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar Credenciais (Opcional):**
    Para rodar o script de ingestão real, adicione seu `credentials.json` na raiz (não versionado por segurança).

3.  **Executar Pipeline:**
    ```bash
    # 1. Preparação
    python scripts/data_prep.py
    
    # 2. Análise de Elasticidade
    python scripts/eda_rgm.py
    
    # 3. Otimização e Recomendação
    python scripts/optimization.py
    ```

## 📊 Highlights da Solução

*   **Arquitetura:** ELT no Google Cloud Platform (Storage + BigQuery).
*   **Modelagem:** Regressão Log-Linear para estimativa de elasticidade-preço.
*   **Estratégia:** Recomendação de **Manutenção de Preço** (não dar descontos) devido à inelasticidade da demanda identificada, protegendo a margem da companhia.
