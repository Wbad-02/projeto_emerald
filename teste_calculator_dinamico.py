import os
from core.extractors.balancete import BalanceteTxtExtractor
from core.utils.calculator import FinancialCalculator

def testar_fluxo_completo():
    pasta = r"C:\Users\Wemerson Dias\Downloads"
    arquivos = ["Balancete-Itasul-2023.csv", "Balancete-Itasul-2024 (1).csv"]
    dados_carregados = {}

    print(f"📂 Lendo arquivos de: {pasta}")

    for arq in arquivos:
        caminho = os.path.join(pasta, arq)
        if not os.path.exists(caminho):
            print(f"❌ Arquivo não encontrado: {arq}")
            continue
            
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # EXECUTA O SEU EXTRATOR REAL
            extrator = BalanceteTxtExtractor(conteudo)
            resultado_extracao = extrator.execute()
            
            ano = resultado_extracao["metadata"].get("ano")
            if ano:
                dados_carregados[ano] = {"balancete": resultado_extracao}
                print(f"✅ {arq} processado dinamicamente para o ano {ano}")

    # CHAMA A CALCULADORA COM O RESULTADO DA EXTRAÇÃO
    if len(dados_carregados) >= 2:
        relatorio = FinancialCalculator.processar_dashboard(dados_carregados)
        
        print("\n" + "="*80)
        print(f"🏢 EMPRESA: {relatorio['empresa']}")
        print("="*80)
        print(f"{'CONTA':<25} | {'ANTERIOR':>15} | {'ATUAL':>15} | {'VAR %'}")
        print("-" * 80)
        
        for r in relatorio['tabela']:
            print(f"{r['conta']:<25} | {r['anterior']:>15,.2f} | {r['atual']:>15,.2f} | {r['perc']:>10}%")
            
        print(f"\n📈 LIQUIDEZ CORRENTE: {relatorio['indices']['liquidez_corrente']}")
        print("="*80)
    else:
        print("\n❌ Erro: O extrator não conseguiu recuperar dados suficientes dos arquivos.")

if __name__ == "__main__":
    testar_fluxo_completo()