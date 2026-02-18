import os
from core.extractors.balancete import BalanceteTxtExtractor
from core.extractors.dre import DreTxtExtractor
from core.utils.converter import FileConverter

def formatar_moeda(valor):
    """Formatação visual para o terminal."""
    cor = "\033[92m" if valor >= 0 else "\033[91m"
    reset = "\033[0m"
    return f"{cor}R$ {valor:>15,.2f}{reset}"

def testar_sistema():
    print(f"\n{'='*70}\n   INSPEÇÃO DE DADOS - PROJETO EMERALD (GRAU 1)\n{'='*70}")
    
    diretorio = "uploads"
    for arquivo in os.listdir(diretorio):
        caminho = os.path.join(diretorio, arquivo)
        
        # 1. Conversão e Identificação
        with open(caminho, 'rb') as f:
            from types import SimpleNamespace
            mock_file = SimpleNamespace(filename=arquivo, read=f.read, seek=f.seek)
            texto = FileConverter.to_text_stream(mock_file)

        # Identificação por Regex (Clean Code: isolar lógica de decisão)
        is_dre = any(k in arquivo.upper().replace('.', '').replace('-', '') for k in ['DRE', 'RESULTADO'])
        
        extrator = DreTxtExtractor(texto) if is_dre else BalanceteTxtExtractor(texto)
        dados = extrator.execute()
        
        # 2. Exibição Visual Separada por Tipo
        print(f"\n📄 ARQUIVO: {arquivo}")
        print(f"🏢 EMPRESA: {dados['metadata']['empresa']}")
        print(f"📅 ANO:     {dados['metadata']['ano']}")
        print(f"🛠️ TIPO:    {'[ DRE ]' if is_dre else '[ BALANCETE ]'}")
        print("-" * 40)

        # Seleciona o dicionário correto baseado no tipo
        indicadores = dados.get('indicadores_grau_1') if is_dre else dados.get('resumo_grau_1')
        
        if indicadores:
            for k, v in indicadores.items():
                print(f"  {k:.<30} {formatar_moeda(v)}")
        else:
            print("  ⚠️ NENHUM INDICADOR ENCONTRADO.")
        print("-" * 70)

if __name__ == "__main__":
    testar_sistema()