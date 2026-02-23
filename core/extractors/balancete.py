import re
import csv
import io
import unicodedata

class BalanceteTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.resumo_grau_1 = {}
        self.metadata = {
            "empresa": "Não Identificada", 
            "ano": None, 
            "cnpj": "Não Identificado"
        }
        # Mapeamento de Grau 1 conforme padrão Itasul
        self.MAPA_SISTEMA = {
            "1": "Ativo Total", 
            "1.1": "Ativo Circulante", 
            "1.2": "Ativo Não Circulante",
            "2": "Passivo Total", 
            "2.1": "Passivo Circulante", 
            "2.2": "Passivo Não Circulante",
            "2.3": "Patrimônio Líquido"
        }

    def _normalizar(self, texto):
        if not texto: return ""
        nfkd = unicodedata.normalize('NFKD', texto)
        return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper()

    def _parse_currency(self, s, cod):
        """Trata números como 1,354,734.47d (Padrão Itasul)"""
        if not s or str(s).strip() in ['0.00', '0,00', '-', '']: return 0.0
        
        s_clean = str(s).lower().strip()
        # Identifica se é Débito ou Crédito no final da string
        is_debito = 'd' in s_clean
        is_credito = 'c' in s_clean
        
        # Remove separadores de milhar (vírgula) e mantém o ponto decimal
        num_only = s_clean.replace(',', '')
        num_only = re.sub(r'[^\d.]', '', num_only)
            
        try:
            val = float(num_only)
            # Lógica Contábil: Ativo (1) é Devedor (+), Passivo (2) é Credor (+)
            # Se uma conta de Passivo/PL (2) tiver 'd', ela está negativa
            if cod.startswith('2'):
                return val if is_credito else -val
            return val if is_debito else -val
        except: return 0.0

    def execute(self):
        f = io.StringIO(self.content)
        reader = csv.reader(f)
        
        for partes in reader:
            if not partes: continue
            
            line_str = " ".join(partes).upper()
            line_norm = self._normalizar(line_str)

            # 1. CAPTURA DE EMPRESA (Somente a primeira ocorrência)
            if "EMPRESA:" in line_norm and self.metadata["empresa"] == "Não Identificada":
                for p in partes:
                    if len(p.strip()) > 5 and "EMPRESA" not in p.upper():
                        self.metadata["empresa"] = p.strip().upper()
                        break

            # 2. CAPTURA DE CNPJ (Trava na primeira ocorrência para evitar o rodapé)
            if "C.N.P.J.:" in line_norm and self.metadata["cnpj"] == "Não Identificado":
                match_cnpj = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', line_str)
                if match_cnpj:
                    self.metadata["cnpj"] = match_cnpj.group(1)

            # 3. CAPTURA DE ANO
            if "PERIODO:" in line_norm and not self.metadata["ano"]:
                match_ano = re.search(r'(\b202[0-9]\b)', line_norm)
                if match_ano: 
                    self.metadata["ano"] = match_ano.group(1)

            # 4. CAPTURA DE VALORES (Foco na Coluna 13 - Saldo Atual)
            if len(partes) >= 14:
                classificacao = partes[1].strip()
                if classificacao in self.MAPA_SISTEMA:
                    # O Saldo Atual no seu CSV está no índice 13
                    valor_extraido = self._parse_currency(partes[13], classificacao)
                    self.resumo_grau_1[self.MAPA_SISTEMA[classificacao]] = valor_extraido

        return {
            "metadata": self.metadata, 
            "resumo_grau_1": self.resumo_grau_1
        }