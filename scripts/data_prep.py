import pandas as pd
import numpy as np
import os

# Configuração de Paths
BASE_PATH = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados"
OUTPUT_PATH = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\processed"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def load_data():
    print("Carregando dados...")
    sales = pd.read_csv(os.path.join(BASE_PATH, "sales_data.csv"))
    stores = pd.read_csv(os.path.join(BASE_PATH, "stores.csv"))
    comp = pd.read_csv(os.path.join(BASE_PATH, "competitor_data.csv"))
    return sales, stores, comp

def clean_sales(df):
    print("Limpando Vendas...")
    # Converter datas
    df['date_order'] = pd.to_datetime(df['date_order'], errors='coerce')
    
    # Remover ruídos (Padrão do case: dados incompletos/ruidosos)
    # 1. Preços ou custos negativos/zerados
    df = df[(df['unit_price'] > 0) & (df['total_cost'] > 0)]
    
    # 2. Remover nulos em chaves essenciais
    df = df.dropna(subset=['sale_id', 'product_id', 'store_id', 'date_order'])
    
    # 3. Garantir consistência numérica
    # Recalcular revenue se necessário ou confiar? Vamos confiar mas verificar outliers
    df['calculated_revenue'] = df['units_sold'] * df['unit_price_after_discount']
    
    return df

def clean_competitor(df):
    print("Limpando Concorrentes...")
    df['datetime_extraction'] = pd.to_datetime(df['datetime_extraction'], errors='coerce')
    df['date'] = df['datetime_extraction'].dt.date
    
    # Remover preços negativos
    df = df[df['competitor_price'] > 0]
    
    # Agregar por dia/produto (média de preço no dia)
    # Opcional: Filtrar apenas pagamentos 'à vista' (pay_type=1) se for a regra, mas vamos fazer média geral por enquanto
    df_agg = df.groupby(['product_id', 'date'])['competitor_price'].mean().reset_index()
    df_agg['date'] = pd.to_datetime(df_agg['date'])
    return df_agg

def master_table(sales, stores, comp):
    print("Criando Tabela Mestra...")
    
    # Join com Stores
    master = sales.merge(stores, on='store_id', how='left')
    
    # Join com Competitors (Asof merge ou left join na data)
    # Vamos fazer um Left Join na data exata. Se não houver preço no dia, forward fill depois.
    master = master.sort_values('date_order')
    comp = comp.sort_values('date')
    
    master = pd.merge_asof(master, comp, 
                           left_on='date_order', 
                           right_on='date', 
                           by='product_id', 
                           direction='backward', # Pega o preço mais recente do concorrente
                           suffixes=('', '_comp'))
    
    # Feature Engineering Básico
    master['month'] = master['date_order'].dt.month
    master['week'] = master['date_order'].dt.isocalendar().week
    master['price_gap_percent'] = (master['unit_price_after_discount'] - master['competitor_price']) / master['competitor_price']
    
    return master

if __name__ == "__main__":
    sales, stores, comp = load_data()
    
    sales_clean = clean_sales(sales)
    comp_clean = clean_competitor(comp)
    
    final_df = master_table(sales_clean, stores, comp_clean)
    
    output_file = os.path.join(OUTPUT_PATH, "master_table.parquet")
    final_df.to_parquet(output_file, index=False)
    
    print(f"Dados processados salvos em: {output_file}")
    print(f"Linhas finais: {len(final_df)}")
    print(final_df.head())
