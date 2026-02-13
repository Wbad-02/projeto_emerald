from core.utils.calculator import FinancialCalculator

# Simulação do objeto 'dados_por_ano' gerado pelo app.py
dados_mock = {
    "2023": {
        "balancete": {
            "resumo_grau_1": {
                "1": {"valor": 3152485.89},      # Ativo Total 2023
                "1.1": {"valor": 2083095.12},    # Ativo Circulante 2023
                "2.3": {"valor": -934436.80}     # PL 2023
            }
        },
        "dre": {
            "indicadores_grau_1": {
                "RECEITA BRUTA": 5489982.36
            }
        }
    },
    "2024": {
        "balancete": {
            "resumo_grau_1": {
                "1": {"valor": 3500000.00},      # Ativo Total 2024
                "1.1": {"valor": 2500000.00},    # Ativo Circulante 2024
                "2.3": {"valor": -1000000.00}    # PL 2024
            }
        },
        "dre": {
            "indicadores_grau_1": {
                "RECEITA BRUTA": 6000000.00
            }
        }
    }
}

print(f"\n{'='*80}")
print(f"🧪 TESTE DE UNIDADE: CALCULADORA FINANCEIRA")
print(f"{'='*80}")

# Executa o cálculo
resultado = FinancialCalculator.gerar_tabela_comparativa(dados_mock)

if not resultado:
    print("❌ ERRO: A calculadora não gerou dados. Verifique os anos no dicionário.")
else:
    print(f"{'CONTA':<25} | {'2023':<12} | {'2024':<12} | {'VARIAÇÃO':<12} | {'STATUS'}")
    print("-" * 80)
    
    for item in resultado:
        # Só imprime se houver algum valor para não poluir o teste
        if item['anterior'] != 0 or item['atual'] != 0:
            status = f"{item['status_percentual']:+.1f}%"
            print(f"{item['conta']:<25} | {item['anterior']:>12,.2f} | {item['atual']:>12,.2f} | {item['variacao']:>12,.2f} | {status}")

print(f"\n{'='*80}")