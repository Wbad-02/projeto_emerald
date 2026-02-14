import os
from werkzeug.datastructures import FileStorage
from core.utils.converter import FileConverter

def diagnostico_completo(caminho):
    print(f"\n{'='*80}")
    print(f"🔍 DIAGNÓSTICO DE TEXTO BRUTO (PÓS-CONVERTER)")
    print(f"{'='*80}")

    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return

    # 1. Executa o Converter (Simula o upload)
    with open(caminho, 'rb') as f:
        arquivo_mock = FileStorage(f, filename=os.path.basename(caminho))
        texto_puro = FileConverter.to_text_stream(arquivo_mock)

    # 2. Imprime o resultado integral
    print("--- INÍCIO DO TEXTO ---")
    print(texto_puro)
    print("--- FIM DO TEXTO ---")

    # 3. Teste de Sanidade específico para a conta ATIVO
    print(f"\n{'='*80}")
    print(f"🎯 BUSCA ESPECÍFICA PELA LINHA DO ATIVO")
    print(f"{'='*80}")
    
    linhas = texto_puro.splitlines()
    for i, linha in enumerate(linhas):
        # Procura a linha que define o ATIVO (Classificação 1)
        if ",1," in linha or "1,ATIVO" in linha:
            print(f"Linha {i}: {linha}")

# Substitua pelo seu caminho real
caminho_balancete = r"C:\Users\Wemerson Dias\Downloads\Balancete-Itasul-2024 (1).csv"
diagnostico_completo(caminho_balancete)