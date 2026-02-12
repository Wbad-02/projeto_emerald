import pandas as pd
import re
import io

class BalanceteCsvExtractor:
    def __init__(self, file):
        self.file = file
        self.metadata = {"empresa": "Não Identificado", "cnpj": "Não Identificado"}

    def execute(self):
        try:
            content = self.file.read()
            self.file.seek(0)
            df = pd.read_csv(io.BytesIO(content), header=None, sep=',', encoding='utf-8', quotechar='"')
        except:
            self.file.seek(0)
            df = pd.read_csv(self.file, header=None, sep=',', encoding='latin1', quotechar='"')

        self._extract_metadata(df)
        flat_data = self._parse_financial_rows(df)

        return {
            "metadata": self.metadata,
            "contas": self._build_hierarchy(flat_data)
        }

    def _extract_metadata(self, df):
        if len(df) > 0:
            self.metadata["empresa"] = str(df.iloc[0, 1]).strip()
        if len(df) > 1:
            self.metadata["cnpj"] = str(df.iloc[1, 1]).strip()

    def _parse_financial_rows(self, df):
        rows = []
        for i, row in df.iterrows():
            if i < 7: continue
            
            classif = str(row[1]).strip() if pd.notna(row[1]) else ""
            desc = str(row[3]).strip() if pd.notna(row[3]) else ""
            
            if re.match(r'^(\d+\.?)+$', classif) and len(desc) > 2:
                rows.append({
                    "classificacao": classif,
                    "descricao": desc,
                    "nivel": classif.count('.'),
                    "valores": {
                        "saldo_anterior": self._to_float(row[7]),
                        "saldo_atual": self._to_float(row[13])
                    }
                })
        return rows

    def _to_float(self, val):
        if pd.isna(val): return 0.0
        s = str(val).strip().lower()
        is_negative = '(' in s or '-' in s
        # Formato Balancete (Americano): 1,234.56
        s = re.sub(r'[^\d.]', '', s.replace(',', ''))
        try:
            num = float(s)
            return -num if is_negative else num
        except: return 0.0

    def _build_hierarchy(self, flat_data):
        root, stack = [], []
        for row in flat_data:
            node = {**row, "filhos": []}
            while stack and row['nivel'] <= stack[-1]['nivel']:
                stack.pop()
            if not stack:
                root.append(node)
            else:
                stack[-1]['filhos'].append(node)
            stack.append(node)
        return root