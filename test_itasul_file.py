import os
from balancete import BalanceteTxtExtractor

def test_extract_from_file():
    # Caminho fornecido pelo usuário
    path = r"C:\Users\Wemerson Dias\Downloads\Balancete-Itasul-2023.csv"
    
    if not os.path.exists(path):
        print(f"❌ Erro: Arquivo não encontrado em {path}")
        return

    print(f"📂 Abrindo arquivo: {path}")
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Inicializa o extrator com o conteúdo real
    extractor = BalanceteTxtExtractor(content)
    resultado = extractor.execute()

    print("\n--- 📊 RESULTADOS DA EXTRAÇÃO REAL ---")
    print(f"Empresa: {resultado['metadata']['empresa']}")
    print(f"Ano: {resultado['metadata']['ano']}")
    
    # Validação dos Pilares do Dashboard
    pilares = ["Ativo Total", "Ativo Circulante", "Passivo Total", "Patrimônio Líquido"]
    
    for pilar in pilares:
        valor = resultado['resumo_grau_1'].get(pilar, 0.0)
        # Formata para padrão brasileiro na exibição do terminal
        print(f"✅ {pilar}: R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    print("\n--- 📋 PRIMEIRAS 5 CONTAS DETALHADAS ---")
    for conta in resultado['contas'][:5]:
        print(f"Código: {conta['classificacao']} | Desc: {conta['descricao']} | Valor: {conta['valor']}")

if __name__ == "__main__":
    test_extract_from_file()