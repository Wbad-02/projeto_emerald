import re
import csv
import io
import unicodedata

class DreTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.indicadores = {
            "RECEITA BRUTA": 0.0, "RECEITA LIQUIDA": 0.0, "LUCRO BRUTO": 0.0,
            "DESPESAS OPERACIONAIS": 0.0, "RESULTADO OPERACIONAL": 0.0,
            "LUCRO DO EXERCICIO": 0.0
        }
        self.metadata = {"ano": None, "empresa": "Não Identificada", "cnpj": "Não Identificado"}

    def _normalizar(self, texto):
        if not texto: return ""
        nfkd = unicodedata.normalize('NFKD', texto)
        return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper()

    def _limpar_valor(self, val_str):
        """Trata o padrão Itasul: 5,014,213.27 ou (601,705.46)"""
        if not val_str: return 0.0
        
        clean = val_str.strip()
        negativo = "(" in clean or "-" in clean
        
        # Remove tudo que não seja número ou ponto decimal
        # No seu CSV, a vírgula é separador de milhar e o ponto é decimal
        clean = clean.replace(',', '') 
        clean = re.sub(r'[^\d.]', '', clean)
        
        try:
            valor = float(clean)
            return -valor if negativo else valor
        except:
            return 0.0

    def execute(self):
        f = io.StringIO(self.content)
        reader = csv.reader(f)
        
        for partes in reader:
            if not partes: continue
            
            line_str = " ".join(partes)
            line_norm = self._normalizar(line_str)
            
            # 1. Metadados
            if "EMPRESA:" in line_norm and self.metadata["empresa"] == "Não Identificada":
                for p in partes:
                    if len(p.strip()) > 5 and "EMPRESA" not in p.upper():
                        self.metadata["empresa"] = p.strip().upper()
                        break

            # CNPJ da ITASUL (Evita pegar o da Upgrade Contabilidade no rodapé)
            if "C.N.P.J.:" in line_norm and self.metadata["cnpj"] == "Não Identificado":
                match_cnpj = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', line_str)
                if match_cnpj: self.metadata["cnpj"] = match_cnpj.group(1)

            if "202" in line_norm and not self.metadata["ano"]:
                match_ano = re.search(r'(\b202[0-9]\b)', line_norm)
                if match_ano: self.metadata["ano"] = match_ano.group(1)

            # 2. CAPTURA POR COLUNA FIXA (Padrão Itasul detectado: Coluna 11)
            # O Saldo Atual está na posição 11 do array 'partes'
            valor = 0.0
            if len(partes) > 11:
                valor = self._limpar_valor(partes[11])

            # 3. Mapeamento
            if "RECEITA BRUTA" in line_norm: 
                self.indicadores["RECEITA BRUTA"] = valor
            elif "RECEITA" in line_norm and ("LIQUIDA" in line_norm or "QUIDA" in line_norm): 
                self.indicadores["RECEITA LIQUIDA"] = valor
            elif "LUCRO BRUTO" in line_norm: 
                self.indicadores["LUCRO BRUTO"] = valor
            elif "DESPESAS OPERACIONAIS" in line_norm:
                self.indicadores["DESPESAS OPERACIONAIS"] = valor
            elif "RESULTADO OPERACIONAL" in line_norm:
                self.indicadores["RESULTADO OPERACIONAL"] = valor
            elif "LUCRO" in line_norm and ("LIQUIDO DO EXERCICIO" in line_norm or "LIQUIDO DO PERIODO" in line_norm):
                self.indicadores["LUCRO DO EXERCICIO"] = valor

        return {"metadata": self.metadata, "indicadores_grau_1": self.indicadores}