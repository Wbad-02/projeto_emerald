import os

from werkzeug.datastructures import FileStorage

from core.extractors.balancetes.balancete_csv import BalanceteCsvExtractor

# Caminho do arquivo que apresentou erro de captura no Passivo
FILE_PATH = r"exemplos/Balancete2025.csv"


def testar_extracao_completa():
    print("--- 🧪 TESTE DE EXTRAÇÃO INTEGRAL: BALANCETE ---")

    if not os.path.exists(FILE_PATH):
        print(f"❌ Erro: Arquivo não encontrado em {FILE_PATH}")
        return

    with open(FILE_PATH, "rb") as f:
        storage = FileStorage(stream=f, filename=os.path.basename(FILE_PATH))
        extrator = BalanceteCsvExtractor(storage)
        resultado = extrator.execute()

    resumo = resultado.get("resumo_grau_1", {})

    print("\n1. METADADOS:")
    print(f"   - Empresa: {resultado.get('metadata', {}).get('empresa')}")
    print(f"   - Ano: {resultado.get('metadata', {}).get('ano')}")

    print("\n2. VALORES CAPTURADOS (RESUMO GRAU 1):")
    for conta, valor in resumo.items():
        status = "✅ OK" if valor != 0 else "❌ ZERADO/NÃO ENCONTRADO"
        print(f"   - {conta}: {valor} | {status}")


if __name__ == "__main__":
    testar_extracao_completa()
