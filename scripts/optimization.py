import pandas as pd
import numpy as np
import os

# Configuração de Paths
DATA_PATH = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\processed\master_table.parquet"
ELASTICITY_PATH = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\results\elasticities.csv"
OUTPUT_DIR = r"C:\Users\david\OneDrive\Documentos\David Arquivos\Meu projetos\Americanas_case_v3\dados\results"

def load_data():
    df = pd.read_parquet(DATA_PATH)
    elas = pd.read_csv(ELASTICITY_PATH)
    return df, elas

def get_baseline_metrics(df):
    """
    Calcula métricas basais por produto E REGIÃO.
    """
    baseline = df.groupby(['product_id', 'region']).agg({
        'unit_price_after_discount': 'mean', # Preço praticado atual
        'total_cost': 'sum',
        'units_sold': 'sum',
        'total_revenue': 'sum'
    }).reset_index()
    
    baseline['avg_cost'] = baseline['total_cost'] / baseline['units_sold']
    baseline['avg_price'] = baseline['unit_price_after_discount']
    baseline['current_profit'] = baseline['total_revenue'] - baseline['total_cost']
    
    return baseline

def simulate_scenarios(baseline, elasticities):
    results = []
    
    # Merge com elasticidades (JOIN agora por Produto e Região)
    merged = baseline.merge(elasticities, on=['product_id', 'region'], how='inner')
    
    discounts = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    
    print(f"Simulando cenários para {len(merged)} combinações Produto-Região...")
    
    for _, row in merged.iterrows():
        product = row['product_id']
        region = row['region']
        elasticity = row['own_price_elasticity']
        base_price = row['avg_price']
        base_cost = row['avg_cost']
        base_units = row['units_sold']
        base_profit = row['current_profit']
        
        # Cenário Base
        results.append({
            'product_id': product,
            'region': region,
            'scenario': 'Base',
            'discount': 0.0,
            'new_price': base_price,
            'predicted_units': base_units,
            'revenue': row['total_revenue'],
            'profit': base_profit,
            'incremental_profit': 0,
            'roi': 0
        })
        
        # Cenários de Desconto
        for d in discounts:
            new_price = base_price * (1 - d)
            price_ratio = new_price / base_price
            
            # Previsão baseada em elasticidade
            predicted_units = base_units * (price_ratio ** elasticity)
            
            new_revenue = predicted_units * new_price
            new_cost = predicted_units * base_cost
            new_profit = new_revenue - new_cost
            
            incremental_profit = new_profit - base_profit
            
            investment = (base_price - new_price) * predicted_units
            roi = (incremental_profit / investment) if investment > 0 else 0
            
            results.append({
                'product_id': product,
                'region': region,
                'scenario': f'Discount {int(d*100)}%',
                'discount': d,
                'new_price': new_price,
                'predicted_units': predicted_units,
                'revenue': new_revenue,
                'profit': new_profit,
                'incremental_profit': incremental_profit,
                'roi': roi
            })
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    df, elas = load_data()
    
    baseline = get_baseline_metrics(df)
    scenarios = simulate_scenarios(baseline, elas)
    
    if scenarios.empty:
        print("Nenhum cenário gerado. Verifique se o merge de elasticidade (produto+região) funcionou.")
    else:
        # Encontrar melhor cenário por Produto/Região
        best_scenarios = scenarios.loc[scenarios.groupby(['product_id', 'region'])['incremental_profit'].idxmax()]
        
        # Recomendações: Apenas onde Lucro Incremental > 0 e Discount > 0
        recommendations = best_scenarios[(best_scenarios['incremental_profit'] > 100) & (best_scenarios['discount'] > 0)]
        recommendations = recommendations.sort_values('incremental_profit', ascending=False)
        
        print("\nMelhores Oportunidades por Região (Top 5):")
        cols = ['product_id', 'region', 'scenario', 'new_price', 'predicted_units', 'incremental_profit', 'roi']
        print(recommendations[cols].head(10))
        
        # Salvar
        scenarios.to_csv(os.path.join(OUTPUT_DIR, "scenarios_simulation.csv"), index=False)
        recommendations.to_csv(os.path.join(OUTPUT_DIR, "final_recommendations.csv"), index=False)
        print(f"\nRecomendações salvas em {OUTPUT_DIR}")
