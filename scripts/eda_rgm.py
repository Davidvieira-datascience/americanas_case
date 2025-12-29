import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de Paths
DATA_PATH = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\processed\master_table.parquet"
OUTPUT_DIR = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\results"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_data():
    return pd.read_parquet(DATA_PATH)

def calculate_elasticity(df):
    """
    Calcula elasticidade-preço usando Regressão Log-Log com Numpy:
    ln(Demand) = alpha + beta * ln(Price) + gamma * ln(CompetitorPrice) + error
    AGORA COM GRANULARIDADE POR REGIÃO
    """
    results = []
    
    # Criar chave composta para iteração
    df['key'] = df['product_id'] + "_" + df['region']
    unique_keys = df['key'].unique()
    
    print(f"Calculando elasticidade para {len(unique_keys)} combinações de Produto/Região...")
    
    for key in unique_keys:
        prod_region_df = df[df['key'] == key].copy()
        
        if prod_region_df.empty:
            continue

        # Obter identificadores originais
        try:
            product_id = prod_region_df['product_id'].iloc[0]
            region = prod_region_df['region'].iloc[0]
        except IndexError:
            continue
        
        # Regra de corte: Mínimo de pontos de dados
        if len(prod_region_df) < 50: # Aumentei um pouco pois agora é mais específico
            continue
            
        # Log Transformation
        prod_region_df['ln_demand'] = np.log(prod_region_df['units_sold'] + 1)
        prod_region_df['ln_price'] = np.log(prod_region_df['unit_price_after_discount'])
        prod_region_df['ln_comp_price'] = np.log(prod_region_df['competitor_price'] + 1)
        
        # Tratamento de nulos/infinitos
        prod_region_df = prod_region_df.replace([np.inf, -np.inf], np.nan).dropna(subset=['ln_demand', 'ln_price', 'ln_comp_price'])
        
        if len(prod_region_df) < 20: 
            # Precisa de variância para o modelo rodar
            continue
            
        # Matriz X e vetor y
        X = np.column_stack([np.ones(len(prod_region_df)), prod_region_df['ln_price'], prod_region_df['ln_comp_price']])
        y = prod_region_df['ln_demand'].values
        
        try:
            params, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
            
            elasticity = params[1]
            cross_elasticity = params[2]
            
            # R2
            y_mean = np.mean(y)
            ss_tot = np.sum((y - y_mean)**2)
            ss_res = residuals[0] if len(residuals) > 0 else np.sum((y - (X @ params))**2)
            r_squared = 1 - (ss_res / ss_tot)
            
            results.append({
                'product_id': product_id,
                'region': region,
                'own_price_elasticity': elasticity,
                'cross_price_elasticity': cross_elasticity,
                'r_squared': r_squared,
                'sample_size': len(prod_region_df)
            })
        except Exception as e:
            # print(f"Erro no grupo {key}: {e}") # Verbose off
            continue
            
    return pd.DataFrame(results)

def eda_summary(df):
    # Vendas por Categoria/Produto
    print("\nResumo de Vendas por Produto:")
    summary = df.groupby('product_id').agg({
        'units_sold': 'sum',
        'total_revenue': 'sum',
        'profit': lambda x: x.sum() if 'profit' in df.columns else (df['total_revenue'] - df['total_cost']).sum()
    }).sort_values('total_revenue', ascending=False)
    print(summary.head())
    
    return summary

if __name__ == "__main__":
    df = load_data()
    
    # Criar coluna de Lucro se não existir
    if 'profit' not in df.columns:
        df['profit'] = df['total_revenue'] - df['total_cost']

    # 1. EDA Rápida
    summary = eda_summary(df)
    
    # 2. Calcular Elasticidades
    elasticities = calculate_elasticity(df)
    
    # Salvar resultados
    elasticities.to_csv(os.path.join(OUTPUT_DIR, "elasticities.csv"), index=False)
    
    if not elasticities.empty:
        print("\nElasticidades Calculadas (Top 5 mais elásticos - Preço aumenta, venda cai muito):")
        # Mais elásticos são números mais negativos (ex: -3.0 < -0.5)
        print(elasticities.sort_values('own_price_elasticity').head(5))
        
        print("\nProdutos com maior Elasticidade Cruzada (Preço do concorrente sobe, minha venda sobe):")
        print(elasticities.sort_values('cross_price_elasticity', ascending=False).head(5))
    else:
        print("Nenhuma elasticidade pode ser calculada.")

    # Gerar Gráfico de Dispersão Exemplo para o Produto mais vendido
    if not summary.empty:
        top_product = summary.index[0]
        prod_data = df[df['product_id'] == top_product]
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=prod_data, x='unit_price_after_discount', y='units_sold', alpha=0.6)
        plt.title(f'Curva de Demanda - Produto {top_product}')
        plt.xlabel('Preço Final')
        plt.ylabel('Unidades Vendidas')
        plt.savefig(os.path.join(OUTPUT_DIR, f"demanda_{top_product}.png"))
        print(f"Gráfico salvo em {OUTPUT_DIR}")
