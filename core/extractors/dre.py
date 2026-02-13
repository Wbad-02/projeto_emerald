import re
import unicodedata

class DreTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        # Lista de âncoras (usaremos normalização para comparar)
        self.ancoras_grau_1 = [
            "RECEITA BRUTA", "DEDUCOES", "RECEITA LIQUIDA", "CMV", 
            "LUCRO BRUTO", "DESPESAS OPERACIONAIS", "DESPESAS COM VENDAS", 
            "DESPESA COM PESSOAL", "DESPESAS ADMINISTRATIVAS", 
            "DESPESAS TRIBUTARIAS", "DESPESAS FINANCEIRAS", 
            "RESULTADO OPERACIONAL", "RECEITAS NAO OPERACIONAIS"
        ]
        self.metadata = {"empresa": "", "cnpj": ""}

    def _normalizar(self, texto):
        """Remove acentos e deixa em maiúsculo para comparação segura"""
        texto = unicodedata.normalize('NFD', texto)
        texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
        return texto.upper().strip()

    def execute(self):
        lines = self.content.splitlines()
        contas = []
        indicadores_finais = {ancora: 0.0 for ancora in self.ancoras_grau_1}
        
        for line in lines:
            if "Período:" in line or "EXERCÍCIO EM" in line:
                # Pega os 4 últimos dígitos (o ano)
                match_ano = re.search(r'(\d{4})', line)
                if match_ano:
                    self.metadata["ano"] = match_ano.group(1)

        grupo_pai_atual = None
        # Normalizamos as âncoras uma vez só para performance
        ancoras_norm = [self._normalizar(a) for a in self.ancoras_grau_1]

        # Regex robusto para pegar Texto e Valor no final
        regex_linha = re.compile(r'^(.*?)\s{2,}([\(\-]?\d{1,3}(?:\.\d{3})*,\d{2}\)?)$')

        for line in lines:
            line = line.strip()
            if not line or "Descricao" in self._normalizar(line): continue

            match = regex_linha.search(line)
            if match:
                desc_original = match.group(1).strip().upper()
                desc_norm = self._normalizar(desc_original)
                valor = self._parse_br_number(match.group(2))

                # Identifica se a linha é uma Âncora de Grau 1
                is_g1 = False
                ancora_nome = None
                
                for i, a_norm in enumerate(ancoras_norm):
                    # Se a âncora está contida na descrição (ex: "DEDUCOES" em "DEDUÇÕES")
                    if a_norm in desc_norm:
                        is_g1 = True
                        ancora_nome = self.ancoras_grau_1[i]
                        break

                if is_g1:
                    grupo_pai_atual = ancora_nome
                    indicadores_finais[ancora_nome] = valor
                    contas.append({
                        "descricao": desc_original,
                        "valor": valor,
                        "nivel": 1,
                        "pai": None
                    })
                else:
                    contas.append({
                        "descricao": desc_original,
                        "valor": valor,
                        "nivel": 2,
                        "pai": grupo_pai_atual
                    })

        return {
            "metadata": self.metadata,
            "indicadores_grau_1": indicadores_finais,
            "contas": contas
        }

    def _parse_br_number(self, val_str):
        s = val_str.replace('.', '').replace(',', '.')
        if '(' in s: s = "-" + s.replace('(', '').replace(')', '')
        try: return float(s)
        except: return 0.0