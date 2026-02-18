import re
import csv
import io
import unicodedata

class DreTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.indicadores = {
            "RECEITA BRUTA": 0.0, "RECEITA LIQUIDA": 0.0, "LUCRO BRUTO": 0.0,
            "DESPESAS OPERACIONAIS": 0.0, "RESULTADO OPERACIONAL": 0.0
        }
        self.metadata = {"ano": None, "empresa": "Não Identificada"}

    def _normalizar(self, texto):
        """Remove acentos e deixa em maiúsculo para comparação robusta."""
        if not texto: return ""
        nfkd = unicodedata.normalize('NFKD', texto)
        return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper()

    def _limpar_valor(self, val_str):
        if not val_str: return 0.0
        # Remove milhar e trata (1.000,00) como positivo para o dashboard
        clean = val_str.replace(',', '')
        clean = re.sub(r'[^\d.]', '', clean)
        try: return float(clean)
        except: return 0.0

    def execute(self):
        f = io.StringIO(self.content)
        reader = csv.reader(f)
        
        for partes in reader:
            if not partes: continue
            # Normaliza a linha inteira para evitar erros de acentuação
            line_norm = self._normalizar(" ".join(partes))
            
            # 1. Metadados
            if "EMPRESA:" in line_norm:
                for p in partes:
                    if len(p) > 5 and "EMPRESA" not in p.upper():
                        self.metadata["empresa"] = p.strip().upper()
                        break

            match_ano = re.search(r'(\b202[0-9]\b)', line_norm)
            if match_ano: self.metadata["ano"] = match_ano.group(1)

            # 2. Busca o valor (última coluna preenchida que seja numérica)
            valor = 0.0
            for p in reversed(partes):
                if re.search(r'\d', p):
                    valor = self._limpar_valor(p)
                    break

            # 3. Mapeamento Flexível
            if "RECEITA BRUTA" in line_norm: 
                self.indicadores["RECEITA BRUTA"] = valor
            elif "RECEITA" in line_norm and "QUIDA" in line_norm: 
                self.indicadores["RECEITA LIQUIDA"] = valor
            elif "LUCRO BRUTO" in line_norm: 
                self.indicadores["LUCRO BRUTO"] = valor
            elif "DESPESAS" in line_norm and ("OPERAC" in line_norm or "ADMIN" in line_norm):
                self.indicadores["DESPESAS OPERACIONAIS"] = valor
            elif "RESULTADO" in line_norm and ("OPERAC" in line_norm or "EXERC" in line_norm):
                # Captura tanto 'Resultado Operacional' quanto 'Resultado do Exercício'
                self.indicadores["RESULTADO OPERACIONAL"] = valor

        return {"metadata": self.metadata, "indicadores_grau_1": self.indicadores}