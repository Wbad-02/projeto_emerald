import requests
import os

def testar_comparativo_completo():
    url = "http://127.0.0.1:5000/processar"
    
    # Caminho do seu arquivo real de 2023
    caminho_2023 = r"C:\Users\Wemerson Dias\Downloads\Balancete-Itasul-2023.txt"
    
    if not os.path.exists(caminho_2023):
        print("❌ Arquivo não encontrado para o teste.")
        return

    print("🚀 Simulando upload de múltiplos anos (2023 e 2024)...")

    # Abrimos o mesmo arquivo duas vezes, mas mudamos o nome para simular anos diferentes
    with open(caminho_2023, 'rb') as f1, open(caminho_2023, 'rb') as f2:
        files = [
            ('pdf-input', ('balancete_2023.txt', f1, 'text/plain')),
            ('pdf-input', ('balancete_2024.txt', f2, 'text/plain'))
        ]
        
        try:
            response = requests.post(url, files=files)
            dados = response.json()

            print(f"\n✅ Status da Resposta: {response.status_code}")
            
            # Validação da Tabela de 5 Colunas
            if "comparativo" in dados and len(dados["comparativo"]) > 0:
                print(f"✨ SUCESSO: Motor de cálculo gerou {len(dados['comparativo'])} linhas de análise.")
                
                # Mostra a primeira linha como exemplo (Ativo Total)
                item = dados["comparativo"][2] # Geralmente Ativo Total é o terceiro no mapa
                print("\n--- AMOSTRA DA TABELA (JSON) ---")
                print(f"Conta: {item['conta']}")
                print(f"Anterior (2023): R$ {item['anterior']:,.2f}")
                print(f"Atual (2024):    R$ {item['atual']:,.2f}")
                print(f"Variação:        R$ {item['variacao']:,.2f}")
                print(f"Status:          {item['status_percentual']}%")
                print("--------------------------------")
            else:
                print("⚠️ O servidor respondeu, mas a tabela comparativa está vazia.")
                print("Dica: Verifique se o extrator está capturando anos diferentes nos arquivos.")

        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    testar_comparativo_completo()