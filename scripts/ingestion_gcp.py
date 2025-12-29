from google.cloud import bigquery
import pandas as pd
import os

def upload_to_bigquery(dataset_id, table_id, file_path, schema=None):
    """
    Carrega um arquivo CSV para uma tabela do BigQuery.
    
    Args:
        dataset_id (str): ID do dataset no BigQuery.
        table_id (str): Nome da tabela de destino.
        file_path (str): Caminho local do arquivo CSV.
        schema (list): Lista de google.cloud.bigquery.SchemaField (opcional).
    """
    client = bigquery.Client()
    
    # Configuração do job de carga
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True if schema is None else False,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE # Sobrescreve dados existentes
    )

    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, f"{dataset_id}.{table_id}", job_config=job_config)

    print(f"Iniciando carga para {dataset_id}.{table_id}...")
    job.result()  # Aguarda a conclusão do job
    
    table = client.get_table(f"{dataset_id}.{table_id}")
    print(f"Carregado {table.num_rows} linhas para {dataset_id}.{table_id}.")

if __name__ == "__main__":
    # --- CONFIGURAÇÃO REAL ---
    # 1. Substitua pelo ID do seu projeto no GCP
    PROJECT_ID = "americanas-rgm-case" 
    
    # 2. Caminho para sua chave de Conta de Serviço (baixe do Console GCP)
    KEY_PATH = "credentials.json"
    
    DATASET_ID = "raw_data"
    
    # 3. Configurar Cliente com Autenticação
    if os.path.exists(KEY_PATH):
        print(f"Usando credenciais de: {KEY_PATH}")
        client = bigquery.Client.from_service_account_json(KEY_PATH)
    else:
        print(f"⚠️ AVISO: Arquivo '{KEY_PATH}' não encontrado. O script tentará usar credenciais padrão do sistema (gcloud auth application-default login).")
        client = bigquery.Client(project=PROJECT_ID)

    # Criar Dataset se não existir
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} já existe.")
    except Exception:
        print(f"Criando dataset {DATASET_ID}...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US" # Ou southamerica-east1
        client.create_dataset(dataset, timeout=30)

    # Mapeamento de Arquivos
    files = {
        "sales_history": r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\sales_data.csv",
        "competitor_prices": r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\competitor_data.csv",
        "stores": r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\stores.csv"
    }

    # Schemas
    sales_schema = [
        bigquery.SchemaField("sale_id", "STRING"),
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("store_id", "STRING"),
        bigquery.SchemaField("channel", "STRING"),
        bigquery.SchemaField("date_order", "DATE"),
        bigquery.SchemaField("units_sold", "INTEGER"),
        bigquery.SchemaField("unit_price", "FLOAT"),
        bigquery.SchemaField("discount_pct", "FLOAT"),
        bigquery.SchemaField("unit_price_after_discount", "FLOAT"),
        bigquery.SchemaField("total_revenue", "FLOAT"),
        bigquery.SchemaField("total_cost", "FLOAT"),
    ]

    # Execução Real
    try:
        # Importante: Passamos o client autenticado para a função
        # Precisaríamos refatorar a função upload_to_bigquery para aceitar 'client' ou instanciar dentro.
        # Vamos ajustar a função upload_to_bigquery acima para receber o client?
        # Para simplificar este replace, vou redefinir a chamada aqui embaixo de forma direta ou 
        # assumir que quem roda edita a função. 
        # MELHOR ABORDAGEM: Vou apenas chamar a função upload_to_bigquery passando o client como argumento extra se eu mudar a def,
        # mas como não mudei a def lá em cima, vou instanciar o client DENTRO da função usando o enviroment variable.
        
        # Opção mais robusta sem mudar a assinatura da função lá em cima (que usa default client):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH
        print("Variável de ambiente definida para autenticação.")

        upload_to_bigquery(DATASET_ID, "sales_history", files["sales_history"], schema=sales_schema)
        upload_to_bigquery(DATASET_ID, "competitor_prices", files["competitor_prices"]) 
        upload_to_bigquery(DATASET_ID, "stores", files["stores"])
        
        print("\n✅ Carga Real Concluída com Sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")
        print("Verifique se o PROJECT_ID está correto e se o arquivo credentials.json é válido.")
