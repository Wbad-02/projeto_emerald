from core.extractors.balancete import BalanceteTxtExtractor
from core.utils.converter import FileConverter
from werkzeug.datastructures import FileStorage
import os

def check_2024():
    caminho = r"C:\Users\Wemerson Dias\Downloads\origin\uploads\Balancete Itasul 2024.pdf"
    
    with open(caminho, 'rb') as f:
        file_mock = FileStorage(f, filename="Balancete Itasul 2024.pdf")
        texto = FileConverter.to_text_stream(file_mock)
        
    extrator = BalanceteTxtExtractor(texto)
    res = extrator.execute()
    
    print(f"\n🔍 RESULTADO DA EXTRAÇÃO 2024:")
    print(f"📅 Ano Identificado: {res['metadata'].get('ano')}")
    print(f"💰 Ativo Total Encontrado: {res['resumo_grau_1'].get('1', {}).get('valor')}")

if __name__ == "__main__":
    check_2024()