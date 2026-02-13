import requests
import os

def testar_identificacao_ano():
    url = "http://127.0.0.1:5000/processar"
    
    # Use o seu arquivo real de 2023
    caminho_balancete = r"C:\Users\Wemerson Dias\Downloads\Balancete-Itasul-2023.txt"

    print("🚀 Enviando Balancete para teste de identificação de ano...")

    with open(caminho_balancete, 'rb') as f:
        files = [('pdf-input', ('balancete.txt', f, 'text/plain'))]
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            dados = response.json()
            anos_detectados = list(dados['anos'].keys())
            
            print(f"\n✅ Servidor respondeu com sucesso!")
            print(f"📅 Anos identificados pelo servidor: {anos_detectados}")
            
            if "2023" in anos_detectados:
                print("✨ SUCESSO: O arquivo foi mapeado corretamente para a gaveta de 2023.")
                
                # Verifica se o Ativo está lá dentro
                bal = dados['anos']['2023']['balancete']
                if bal:
                    ativo = bal['resumo_grau_1'].get('1', {}).get('valor', 0)
                    print(f"💰 Valor do Ativo em 2023: R$ {ativo:,.2f}")
            else:
                print("❌ ERRO: O ano 2023 não foi detectado no JSON.")
        else:
            print(f"❌ Erro no servidor: {response.status_code}")

if __name__ == "__main__":
    testar_identificacao_ano()