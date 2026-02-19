import os
import json
from core.services.financial_service import FinancialService

class MockFile:
    """Simula o objeto de arquivo do Flask para testes fora do navegador."""
    def __init__(self, full_path):
        self.filename = os.path.basename(full_path)
        self.full_path = full_path
    
    def read(self):
        with open(self.full_path, 'rb') as f:
            return f.read()

def validar_processamento():
    print("="*80)
    print("🚀 EMERALD INTELLIGENCE - TESTE DE PROCESSAMENTO UNIFICADO")
    print("="*80)

    # 1. Configuração dos caminhos (Baseado nos seus logs)
    downloads_path = r"C:\Users\Wemerson Dias\Downloads"
    arquivos_alvo = [
        "D.-R.-E-Itasul-2023.csv",
        "D.-R.-E-Itasuk-2024. (1).csv",
        "Balancete-Itasul-2023.csv",
        "Balancete-Itasul-2024.csv"
    ]

    files_para_processar = []
    for nome in arquivos_alvo:
        caminho_completo = os.path.join(downloads_path, nome)
        if os.path.exists(caminho_completo):
            files_para_processar.append(MockFile(caminho_completo))
            print(f"✅ Arquivo localizado: {nome}")
        else:
            print(f"❌ Arquivo não encontrado: {nome}")

    if len(files_para_processar) < 2:
        print("\n⚠️ Erro: Arquivos insuficientes para comparação entre anos.")
        return

    # 2. Execução do Serviço (O Maestro)
    print("\n⚙️ Processando extração e cálculos...")
    try:
        # Chama a lógica centralizada no FinancialService
        resultado = FinancialService.processar_arquivos(files_para_processar)
        
        if "error" in resultado:
            print(f"\n❗ Alerta do Sistema: {resultado['error']}")
            return

        # 3. Validação dos Resultados
        print("\n" + "="*80)
        print(f"📊 RELATÓRIO CONSOLIDADO: {resultado['empresa']}")
        print("="*80)

        # Índices Patrimoniais (Etapa 3)
        indices = resultado['indices']
        print(f"🔹 Liquidez Corrente: {indices.get('liq_corrente', 0):.2f}")
        print(f"🔹 Endividamento: {indices.get('endiv_geral', 0):.2f}%")

        # Dados da DRE (Etapa 2)
        dre = resultado['dre']
        print(f"\n📈 Performance (Variação {resultado['empresa']}):")
        print(f"   - Receita Bruta: R$ {dre.get('RECEITA_BRUTA_ATUAL', 0):,.2f} ({dre.get('RECEITA_BRUTA_STATUS', '')})")
        print(f"   - Lucro Líquido: R$ {dre.get('LUCRO_LIQ_ATUAL', 0):,.2f} ({dre.get('LUCRO_LIQ_STATUS', '')})")

        # Tabela Comparativa
        print("\n📝 Tabela de Análise Comparativa:")
        print(f"{'CONTA':<25} | {'ANTERIOR':>15} | {'ATUAL':>15} | {'STATUS'}")
        print("-" * 80)
        for item in resultado['tabela_dre']:
            print(f"{item['conta']:<25} | {item['anterior']:>15,.2f} | {item['atual']:>15,.2f} | {item['status']}")

    except Exception as e:
        print(f"\n💥 Erro Crítico durante o processamento: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    validar_processamento()