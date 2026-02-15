import os
import io
from core.services.financial_service import FinancialService
from core.utils.converter import FileConverter
from core.extractors.dre import DreTxtExtractor
from core.extractors.balancete import BalanceteTxtExtractor

class MockFile(io.BytesIO):
    """Simula um FileStorage do Flask com suporte a seek e filename."""
    def __init__(self, full_path):
        with open(full_path, 'rb') as f:
            super().__init__(f.read())
        self.filename = os.path.basename(full_path)

def realizar_triagem():
    print("🔍 INICIANDO TRIAGEM COMPLETA DO SISTEMA EMERALD\n" + "="*60)

    # 1. Localização dos Arquivos
    pasta = r"C:\Users\Wemerson Dias\Downloads"
    nomes = [
        "D.-R.-E-Itasul-2023.csv",
        "D.-R.-E-Itasuk-2024. (1).csv",
        "Balancete-Itasul-2023.csv",
        "Balancete-Itasul-2024.csv"
    ]
    
    arquivos = []
    for n in nomes:
        p = os.path.join(pasta, n)
        if os.path.exists(p):
            arquivos.append(MockFile(p))
            print(f"✅ Arquivo carregado: {n}")
        else:
            print(f"❌ Falha ao localizar: {n}")

    if not arquivos:
        print("🛑 Nenhum arquivo encontrado para teste.")
        return

    print("\n" + "-"*20 + " ETAPA 1: CONVERSÃO DE TEXTO " + "-"*20)
    for a in arquivos:
        try:
            a.seek(0)
            texto = FileConverter.to_text_stream(a)
            print(f"✅ {a.filename:<30} | {len(texto):>5} caracteres")
        except Exception as e:
            print(f"❌ Erro ao converter {a.filename}: {str(e)}")

    print("\n" + "-"*20 + " ETAPA 2: EXTRAÇÃO DE METADADOS " + "-"*20)
    # Testamos a extração de ano para TODOS os arquivos
    extracao_valida = True
    for a in arquivos:
        try:
            a.seek(0)
            texto = FileConverter.to_text_stream(a)
            # Define extrator baseado no nome
            extrator = DreTxtExtractor(texto) if 'dre' in a.filename.lower() else BalanceteTxtExtractor(texto)
            res = extrator.execute()
            ano = res['metadata'].get('ano')
            
            status = "✅" if ano else "❌"
            print(f"{status} {a.filename:<30} | Ano Detectado: {ano}")
            
            if not ano: extracao_valida = False
        except Exception as e:
            print(f"💥 Falha crítica no extrator para {a.filename}: {str(e)}")
            extracao_valida = False

    print("\n" + "-"*20 + " ETAPA 3: FLUXO COMPLETO DO SERVICE " + "-"*20)
    try:
        # Reseta todos os arquivos para o início antes de enviar ao service
        for a in arquivos: a.seek(0)
        
        resultado = FinancialService.processar_arquivos(arquivos)
        
        if "error" in resultado:
            print(f"⚠️ Alerta do Service: {resultado['error']}")
            print("💡 Dica: Verifique se os arquivos marcados com ❌ na Etapa 2 estão retornando 'None'.")
        else:
            print("✨ SUCESSO TOTAL NO PROCESSAMENTO")
            print(f"   🏢 Empresa: {resultado.get('empresa')}")
            print(f"   📊 Itens Tabela DRE: {len(resultado.get('tabela_dre', []))}")
            print(f"   📝 Itens Tabela Patrimonial: {len(resultado.get('tabela_patrimonial', []))}")
            
    except Exception as e:
        print(f"❌ Erro Crítico no Service: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    realizar_triagem()