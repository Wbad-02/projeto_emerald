import re
import os

class BalanceteTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.resumo_grau_1 = {}
        self.contas = []
        self.metadata = {"empresa": "Não Identificada", "ano": None}
        self.MAPA_SISTEMA = {
            "1": "Ativo Total",
            "1.1": "Ativo Circulante",
            "2": "Passivo Total",
            "2.1": "Passivo Circulante",
            "2.3": "Patrimônio Líquido"
        }

    def _parse_currency_agnostic(self, s, cod):
        if not s or str(s).strip() in ['0.00', '0,00', '-', '""', '']: return 0.0
        s_lower = str(s).lower().strip().replace('"', '')
        is_credito = 'c' in s_lower
        is_negativo = '-' in s_lower or '(' in s_lower
        
        # Lógica Itasul: 3,152,485.89 (vírgula é milhar, ponto é decimal)
        clean = re.sub(r'[^\d,.]', '', s_lower)
        if ',' in clean and '.' in clean:
            clean = clean.replace(',', '') # Remove milhar
        elif ',' in clean:
            clean = clean.replace(',', '.') # Converte padrão BR se houver
            
        try:
            val = abs(float(clean))
            if cod.startswith('1'): return -val if is_credito else val
            if cod.startswith(('2', '6')): return val if is_credito else -val
            return -val if is_negativo else val
        except: return 0.0

    def execute(self):
        lines = self.content.splitlines()
        for line in lines:
            # Captura campos entre aspas conforme seu padrão Itasul
            partes = re.findall(r'"([^"]*)"', line)
            if len(partes) < 14: continue
            
            classificacao = partes[1].strip()
            if not re.match(r'^\d+(\.\d+)*$', classificacao): continue
            
            descricao = partes[3].strip().upper()
            valor_raw = partes[13] # Coluna do Saldo Atual
            valor_final = self._parse_currency_agnostic(valor_raw, classificacao)

            nivel = classificacao.count('.') + 1
            if classificacao in self.MAPA_SISTEMA:
                self.resumo_grau_1[self.MAPA_SISTEMA[classificacao]] = valor_final
            
            self.contas.append({"classificacao": classificacao, "valor": valor_final})
        return {"resumo": self.resumo_grau_1, "total_contas": len(self.contas)}

# --- SCRIPT DE EXECUÇÃO ---
path = r"C:\Users\Wemerson Dias\Downloads\Balancete-Itasul-2023.csv"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    extractor = BalanceteTxtExtractor(content)
    dados = extractor.execute()
    
    print("\n✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("-" * 40)
    for k, v in dados['resumo'].items():
        print(f"{k.ljust(20)}: R$ {v:,.2f}")
    print("-" * 40)
    print(f"Total de linhas processadas: {dados['total_contas']}")
else:
    print(f"❌ Arquivo não encontrado em: {path}")