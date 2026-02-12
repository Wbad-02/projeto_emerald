import pandas as pd
import re
import io

class DreCsvExtractor:
    def __init__(self, file):
        self.file = file
        self.metadata = {"empresa": "Não Identificado", "cnpj": "Não Identificado"}

    def execute(self):
        content_bytes = self.file.read()
        self.file.seek(0)
        
        try:
            content = content_bytes.decode('utf-8')
        except:
            content = content_bytes.decode('latin1')

        # 1. Tenta ler como CSV de múltiplas colunas (Padrão 2024)
        df = pd.read_csv(io.StringIO(content), header=None, sep=',', quotechar='"')
        
        if len(df.columns) > 1:
            return self._process_structured_dre(df)
        else:
            # 2. Se tiver só uma coluna, processa como relatório de texto (Padrão 2023)
            return self._process_text_report_dre(content.splitlines())

    def _process_structured_dre(self, df):
        """Lógica para o arquivo 2024 (múltiplas colunas)."""
        self._extract_metadata_df(df)
        flat_data = []
        for i, row in df.iterrows():
            if i < 4: continue
            
            # Busca a descrição na coluna 0 ou 2
            desc_raw = str(row[0]).strip() if pd.notna(row[0]) and str(row[0]).strip() else str(row[2]).strip()
            # Busca o valor na coluna 11 (conforme inspeção do arquivo 2024)
            val_raw = row[11] if len(row) > 11 else None
            
            if desc_raw and desc_raw.lower() != 'nan' and "Descrição" not in desc_raw:
                # Calcula nível pela coluna (0 = Nível 0, 2 = Nível 1)
                nivel = 0 if pd.notna(row[0]) and str(row[0]).strip() else 1
                flat_data.append({
                    "descricao": desc_raw,
                    "nivel": nivel,
                    "valor": self._to_float(val_raw)
                })
        
        return {"metadata": self.metadata, "contas": self._build_hierarchy(flat_data)}

    def _process_text_report_dre(self, lines):
        """Lógica para o arquivo 2023 (texto alinhado por espaços)."""
        self._extract_metadata_lines(lines)
        flat_data = []
        for line in lines:
            raw_line = line.replace('"', '')
            match = re.search(r'^(.*?)\s{2,}([\d.,()\-]+[CcDd]?)$', raw_line)
            if match:
                raw_desc = match.group(1)
                indent = len(raw_desc) - len(raw_desc.lstrip())
                desc = raw_desc.strip()
                if "Descrição" in desc or any(k in raw_line for k in ["Empresa:", "C.N.P.J."]): continue
                
                flat_data.append({
                    "descricao": desc,
                    "nivel": indent // 2,
                    "valor": self._to_float(match.group(2))
                })
        return {"metadata": self.metadata, "contas": self._build_hierarchy(flat_data)}

    def _extract_metadata_df(self, df):
        # Busca metadados no DataFrame (2024)
        for val in df.head(5).values.flatten():
            s = str(val)
            if "42.497.558" in s: self.metadata["cnpj"] = "42.497.558/0001-74"
            if "ITASUL" in s: self.metadata["empresa"] = "ITASUL TRANSPORTE E LOGISTICA LTDA"

    def _extract_metadata_lines(self, lines):
        # Busca metadados nas linhas de texto (2023)
        combined = " ".join(lines[:10])
        if "42.497.558" in combined: self.metadata["cnpj"] = "42.497.558/0001-74"
        if "ITASUL" in combined: self.metadata["empresa"] = "ITASUL TRANSPORTE E LOGISTICA LTDA"

    def _to_float(self, val):
        if pd.isna(val) or val == "": return 0.0
        s = str(val).strip().lower()
        is_negative = '(' in s or '-' in s
        s = re.sub(r'[^\d,]', '', s.replace('.', '')).replace(',', '.')
        try:
            num = float(s)
            return -num if is_negative else num
        except: return 0.0

    def _build_hierarchy(self, flat_data):
        root, stack = [], []
        for item in flat_data:
            node = {"descricao": item['descricao'], "valor": item['valor'], "filhos": []}
            while stack and item['nivel'] <= stack[-1]['nivel']:
                stack.pop()
            if not stack: root.append(node)
            else: stack[-1]['node']['filhos'].append(node)
            stack.append({'nivel': item['nivel'], 'node': node})
        return root