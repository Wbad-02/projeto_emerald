import re
import csv
import io

class BalanceteTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.resumo_grau_1 = {}
        self.metadata = {"empresa": "Não Identificada", "ano": None}
        self.MAPA_SISTEMA = {
            "1": "Ativo Total", "1.1": "Ativo Circulante", "1.2": "Ativo Não Circulante",
            "2": "Passivo Total", "2.1": "Passivo Circulante", "2.2": "Passivo Não Circulante",
            "2.3": "Patrimônio Líquido"
        }

    def _parse_currency(self, s, cod):
        """Trata números com vírgula como milhar (Padrão Itasul)"""
        if not s or str(s).strip() in ['0.00', '0,00', '-', '']: return 0.0
        
        s_clean = str(s).lower().strip()
        is_credito = 'c' in s_clean
        
        # Remove vírgulas de milhar e mantém o ponto decimal
        # Ex: '3,152,485.89d' -> '3152485.89'
        num_only = s_clean.replace(',', '')
        num_only = re.sub(r'[^\d.]', '', num_only)
            
        try:
            val = float(num_only)
            # Normalização de Sinais
            if cod.startswith(('2', '3')):
                return val if is_credito else -val
            return val if not is_credito else -val
        except: return 0.0

    def execute(self):
        # Usa o leitor de CSV para respeitar as aspas
        f = io.StringIO(self.content)
        reader = csv.reader(f)
        
        for partes in reader:
            if len(partes) < 14: continue
            
            # Captura Empresa e Ano no topo
            line_str = " ".join(partes).upper()
            if "EMPRESA:" in line_str and self.metadata["empresa"] == "Não Identificada":
                self.metadata["empresa"] = partes[1].strip() if len(partes) > 1 else "Não Identificada"
            if "PERÍODO:" in line_str or "/" in line_str:
                match_ano = re.search(r'(\b202[0-9]\b)', line_str)
                if match_ano: self.metadata["ano"] = match_ano.group(1)

            classificacao = partes[1].strip()
            if classificacao in self.MAPA_SISTEMA:
                # No Itasul, o Saldo Atual está na coluna 13
                self.resumo_grau_1[self.MAPA_SISTEMA[classificacao]] = self._parse_currency(partes[13], classificacao)

        return {"metadata": self.metadata, "resumo_grau_1": self.resumo_grau_1}