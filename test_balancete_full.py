import os
from core.extractors.balancete import BalanceteTxtExtractor

# Caminho do arquivo que apresentou erro de captura no Passivo
FILE_PATH = r"C:\Users\Wemerson Dias\Downloads\Balancete2025.csv"

def testar_extracao_completa():
    print(f"--- 🧪 TESTE DE EXTRAÇÃO INTEGRAL: BALANCETE ---")
    
    if not os.path.exists(FILE_PATH):
        print(f"❌ Erro: Arquivo não encontrado em {FILE_PATH}")
        return

    # Lendo o conteúdo bruto para análise
    with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        conteudo = f.read()

    # Executando o extrator
    extrator = BalanceteTxtExtractor(conteudo)
    resultado = extrator.execute()
    
    placeholders = resultado.get("placeholders", {})
    resumo = resultado.get("resumo_grau_1", {})

    print(f"\n1. METADADOS:")
    print(f"   - Empresa: {resultado.get('metadata', {}).get('empresa')}")
    print(f"   - Ano: {resultado.get('metadata', {}).get('ano')}")

    print(f"\n2. VALORES CAPTURADOS (RESUMO GRAU 1):")
    for conta, valor in resumo.items():
        status = "✅ OK" if valor > 0 else "❌ ZERADO/NÃO ENCONTRADO"
        print(f"   - {conta}: {valor} | {status}")

    print(f"\n3. PLACEHOLDERS PARA O DASHBOARD:")
    for key, val in placeholders.items():
        print(f"   => {key}: {val}")

    # Verificação de integridade
    ac = resumo.get("Ativo Circulante", 0)
    pc = resumo.get("Passivo Circulante", 0)
    
    if ac > 0 and pc > 0:
        print("\n✅ SUCESSO: Todos os dados vitais foram capturados!")
    else:
        print("\n🚨 FALHA CRÍTICA: O Passivo ou Ativo não foram lidos. Verifique os nomes das contas no CSV.")

if __name__ == "__main__":
    testar_extracao_completa()