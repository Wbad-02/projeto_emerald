import os
from werkzeug.datastructures import FileStorage
from core.utils.converter import FileConverter
from core.extractors.balancete import BalanceteTxtExtractor

def realizar_teste_balancete(caminho_arquivo):
    print(f"\n{'='*70}")
    print(f"🧪 TESTE DE EXTRAÇÃO: HIERARQUIA E GRAU 1")
    print(f"{'='*70}")

    if not os.path.exists(caminho_arquivo):
        print(f"❌ Erro: Arquivo não encontrado em: {caminho_arquivo}")
        return

    # 1. Preparação e Conversão
    with open(caminho_arquivo, 'rb') as f:
        arquivo_mock = FileStorage(f, filename=os.path.basename(caminho_arquivo))
        texto_limpo = FileConverter.to_text_stream(arquivo_mock)

    # 2. Execução do Extrator
    extrator = BalanceteTxtExtractor(texto_limpo)
    resultado = extrator.execute()
    
    resumo_pai = resultado.get('resumo_grau_1', {})
    contas = resultado.get('contas', [])

    # 3. VALIDAÇÃO DAS VARIÁVEIS DE GRAU 1
    print("\n💎 VARIÁVEIS DE GRAU 1 (PILARES DO BALANCETE):")
    print(f"{'CÓDIGO':<10} | {'DESCRIÇÃO':<30} | {'VALOR FINAL'}")
    print("-" * 60)
    
    for cod, info in resumo_pai.items():
        valor_fmt = f"R$ {info['valor']:,.2f}"
        print(f"{cod:<10} | {info['nome']:<30} | {valor_fmt}")

    # 4. VALIDAÇÃO DA HIERARQUIA (Amostra)
    print("\n📊 ESTRUTURA HIERÁRQUICA (AMOSTRA):")
    print(f"{'NÍVEL':<7} | {'CONTA':<15} | {'DESCRIÇÃO'}")
    print("-" * 60)
    
    # Exibe apenas as primeiras 20 linhas para conferir a "escadinha"
    for conta in contas[:20]:
        indent = "  " * (conta['nivel'] - 1)
        print(f"Grau {conta['nivel']:<2} | {conta['classificacao']:<15} | {indent}{conta['descricao']}")

    print(f"\n✅ Total de contas processadas: {len(contas)}")

# --- CONFIGURAÇÃO DO CAMINHO ---
# Certifique-se de que este caminho aponta para o seu arquivo de balancete
caminho = r"C:\Users\Wemerson Dias\Downloads\Balancete-Itasul-2024 (1).csv"
if __name__ == "__main__":
    realizar_teste_balancete(caminho)