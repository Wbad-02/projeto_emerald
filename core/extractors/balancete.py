import re

class BalanceteTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.resumo_grau_1 = {} 
        self.metadata = {"empresa": "Não Identificada", "cnpj": "", "ano": None}

    def execute(self):
        lines = self.content.splitlines()
        for line in lines:
            # 1. Metadados Dinâmicos (Empresa e Ano)
            if "Empresa:" in line:
                # Pega o texto entre aspas ou após a vírgula
                match = re.search(r'Empresa:,"?([^",]+)"?', line)
                if match: self.metadata["empresa"] = match.group(1).strip()
                continue
                
            if "Período:" in line:
                match_ano = re.search(r'(\d{4})', line)
                if match_ano: self.metadata["ano"] = match_ano.group(1)
                continue

            # 2. Processamento de Contas
            # Procura linhas que começam com o padrão de conta (ex: 010000,1)
            # e captura o último valor da linha (Saldo Atual)
            match_conta = re.search(r'^\d+,([\d.]+),+([^,]+)', line)
            if match_conta:
                classificacao = match_conta.group(1)
                descricao = match_conta.group(2).strip().replace('"', '').upper()
                
                # Pega o último valor numérico antes do fim da linha
                valores = re.findall(r'([\d,.]+)[dc]?,?$', line.strip())
                if valores:
                    valor_raw = valores[-1].rstrip(',')
                    valor_final = self._parse_br_or_us_number(valor_raw, classificacao)

                    nivel = classificacao.count('.') + 1
                    if nivel <= 2:
                        self.resumo_grau_1[classificacao] = {
                            "nome": descricao,
                            "valor": valor_final
                        }

        return {
            "metadata": self.metadata,
            "resumo_grau_1": self.resumo_grau_1
        }

    def _parse_br_or_us_number(self, s, cod):
        """Detecta e converte 3,152,485.89 (2023) ou 3.152.485,89 (2024)"""
        if not s or s in ['0.00', '0,00']: return 0.0
        
        # Remove caracteres de débito/crédito para a conversão
        is_negative = 'c' in s.lower()
        clean = re.sub(r'[^\d,.]', '', s)
        
        # Identifica o separador decimal (o último sinal de pontuação)
        if ',' in clean and '.' in clean:
            if clean.rfind(',') > clean.rfind('.'): # Padrão BR (2024)
                clean = clean.replace('.', '').replace(',', '.')
            else: # Padrão US (2023)
                clean = clean.replace(',', '')
        else:
            clean = clean.replace(',', '.')

        try:
            val = float(clean)
            # Ativo (1): Débito é +, Crédito é - | Passivo (2): Crédito é +, Débito é -
            if cod.startswith('1'): return -val if is_negative else val
            if cod.startswith('2'): return val if is_negative else -val
            return val
        except: return 0.0