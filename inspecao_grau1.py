import os
import io
import re
from core.extractors.balancete import BalanceteTxtExtractor
from core.extractors.dre import DreTxtExtractor
from core.utils.converter import FileConverter

class MockFile(io.BytesIO):
    """Simula um objeto de arquivo com o atributo .filename para o FileConverter."""
    def __init__(self, full_path):
        with open(full_path, 'rb') as f:
            content = f.read()
        super().__init__(content)
        self.filename = os.path.basename(full_path)

def formatar_moeda(valor):
    if valor is None: return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def inspecionar_variaveis():
    print("🔬 INSPEÇÃO DE VARIÁREIS DE GRAU 1 - EMERALD INTELLIGENCE\n" + "="*70)

    pasta = r"C:\Users\Wemerson Dias\Downloads"
    nomes_arquivos = [
        "D.-R.-E-Itasul-2023.csv",
        "Balancete-Itasul-2023.csv"
    ]

    for nome in nomes_arquivos:
        caminho = os.path.join(pasta, nome)
        if not os.path.exists(caminho):
            print(f"❌ Arquivo não localizado: {nome}")
            continue

        try:
            # Uso do MockFile para evitar o AttributeError
            file_mock = MockFile(caminho)
            texto = FileConverter.to_text_stream(file_mock)
            
            print(f"\n📄 ARQUIVO: {nome}")
            print("-" * 40)

            if "DRE" in nome.upper() or "D.-R.-E" in nome.upper():
                extrator = DreTxtExtractor(texto)
                res = extrator.execute()
                dados_g1 = res.get("indicadores_grau_1", {})
                
                print(f"{'INDICADOR DRE':<25} | {'VALOR EXTRAÍDO':>20}")
                for chave, valor in dados_g1.items():
                    print(f"{chave:<25} | {formatar_moeda(valor):>20}")
            
            else:
                extrator = BalanceteTxtExtractor(texto)
                res = extrator.execute()
                dados_g1 = res.get("resumo_grau_1", {})
                
                print(f"{'CÓDIGO':<10} | {'DESCRIÇÃO':<25} | {'VALOR':>20}")
                # Filtra apenas as raízes principais para conferência
                for cod in sorted(dados_g1.keys()):
                    if len(cod) <= 5: # Filtra Grau 1, 2 e 3
                        info = dados_g1[cod]
                        print(f"{cod:<10} | {info['nome'][:25]:<25} | {formatar_moeda(info['valor']):>20}")

        except Exception as e:
            print(f"💥 Erro ao processar {nome}: {str(e)}")

    print("\n" + "="*70 + "\n✅ Inspeção finalizada.")

if __name__ == "__main__":
    inspecionar_variaveis()