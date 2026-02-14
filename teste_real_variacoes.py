import os
import re

# --- LÓGICA DE EXTRAÇÃO E CÁLCULO INCORPORADA PARA O TESTE ISOLADO ---

class LocalExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.resumo = {}
        self.metadata = {"ano": None}

    def execute(self):
        lines = self.content.splitlines()
        for line in lines:
            # Divide por vírgula e limpa aspas
            partes = [p.strip().replace('"', '') for p in line.split(',')]
            
            # 1. Identifica o Ano do Período
            if "Período:" in str(partes):
                match = re.search(r'20\d{2}', line)
                if match: self.metadata["ano"] = match.group()
            
            # 2. Captura Contas (Foco nos índices reais do seu arquivo)
            if len(partes) >= 14:
                classificacao = partes[1]
                # Valida se é um código contábil (ex: 1, 1.1, 2.3)
                if re.match(r'^\d+(\.\d+)*$', classificacao):
                    # SALDO ATUAL REAL ESTÁ NO ÍNDICE 13
                    valor_raw = partes[13]
                    valor_num = self._parse_number(valor_raw, classificacao)
                    
                    nivel = classificacao.count('.') + 1
                    if nivel <= 2:
                        self.resumo[classificacao] = {
                            "nome": partes[3].upper(),
                            "valor": valor_num
                        }
        return {"metadata": self.metadata, "resumo_grau_1": self.resumo}

    def _parse_number(self, s, cod):
        """Trata formato BR (5.175.403,31d) e define sinais financeiros"""
        if not s or s == '0,00': return 0.0
        is_credito = 'c' in s.lower()
        is_debito = 'd' in s.lower()
        
        # Limpeza para conversão float
        clean = s.replace('.', '').replace(',', '.')
        clean = re.sub(r'[^\d.]', '', clean)
        try:
            val = float(clean)
            # Regras de sinal para Ativo (1) vs Passivo/PL (2)
            if cod.startswith('1'): return -val if is_credito else val
            if cod.startswith('2'): return -val if is_debito else val
            return val
        except: return 0.0

class LocalCalculator:
    @staticmethod
    def calcular(dados):
        anos = sorted(dados.keys())
        if len(anos) < 2: return []
        
        ant, atu = anos[0], anos[1]
        p_ant = dados[ant]["balancete"]["resumo_grau_1"]
        p_atu = dados[atu]["balancete"]["resumo_grau_1"]
        
        mapeamento = [
            ("1", "Ativo Total"),
            ("1.1", "Ativo Circulante"),
            ("2.1", "Passivo Circulante"),
            ("2.3", "Patrimônio Líquido")
        ]
        
        resultado = []
        for cod, label in mapeamento:
            v_ant = p_ant.get(cod, {}).get("valor", 0.0)
            v_atu = p_atu.get(cod, {}).get("valor", 0.0)
            
            var = v_atu - v_ant
            # Cálculo de Variação (Etapa 2 do Checklist)
            perc = (var / abs(v_ant) * 100) if v_ant != 0 else 0
            
            resultado.append({
                "conta": label, "anterior": v_ant, "atual": v_atu,
                "variacao": var, "perc": round(perc, 2),
                "status": "▲ Crescimento" if perc > 0.5 else ("▼ Queda" if perc < -0.5 else "● Estável")
            })
        return resultado

# --- EXECUÇÃO DO TESTE REAL ---

def executar_teste():
    pasta = r"C:\Users\Wemerson Dias\Downloads"
    arquivos = ["Balancete-Itasul-2023.csv", "Balancete-Itasul-2024 (1).csv"]
    dados_consolidados = {}

    print(f"\n🚀 TESTE ETAPA 2: EXTRAÇÃO INDEXADA (ÍNDICE 13) E VARIAÇÕES")
    print("-" * 75)

    for nome_arq in arquivos:
        caminho = os.path.join(pasta, nome_arq)
        if not os.path.exists(caminho):
            print(f"⚠️ Não encontrado: {nome_arq}")
            continue

        with open(caminho, 'r', encoding='utf-8') as f:
            texto = f.read()
            extractor = LocalExtractor(texto)
            res = extractor.execute()
            
            ano = res['metadata'].get('ano')
            if ano:
                v_ativo = res['resumo_grau_1'].get('1', {}).get('valor', 0)
                print(f"✅ {nome_arq} -> Ano: {ano} | Ativo Capturado (Final): R$ {v_ativo:,.2f}")
                dados_consolidados[ano] = {"balancete": res}

    if len(dados_consolidados) >= 2:
        print("\n" + "="*95)
        print(f"📊 RESULTADO DA ANÁLISE COMPARATIVA (ITASUL)")
        print("="*95)
        
        comparativo = LocalCalculator.calcular(dados_consolidados)
        
        print(f"{'CONTA':<25} | {'2023':>15} | {'2024':>15} | {'VARIAÇÃO':>15} | {'STATUS'}")
        print("-" * 95)
        
        for i in comparativo:
            print(f"{i['conta']:<25} | {i['anterior']:>15,.2f} | {i['atual']:>15,.2f} | {i['variacao']:>15,.2f} | {i['status']} ({i['perc']}%)")
        print("="*95)
    else:
        print("\n⚠️ Erro: Não foram encontrados dados suficientes de 2023 e 2024.")

if __name__ == "__main__":
    executar_teste()