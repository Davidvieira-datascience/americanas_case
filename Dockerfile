# Usar imagem base leve do Python
FROM python:3.9-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto para o container
# (Scripts e Dados se necessário, embora dados devam vir do GCS em prod)
COPY scripts/ ./scripts/
COPY credentials.json .

# Definir variável de ambiente para credenciais (se usar arquivo local)
# Em produção real no GCP, usa-se Workload Identity, dispensando a chave JSON
ENV GOOGLE_APPLICATION_CREDENTIALS="credentials.json"

# Comando padrão: Rodar a ingestão (pode ser sobrescrito para rodar outros scripts)
CMD ["python", "scripts/ingestion_gcp.py"]
