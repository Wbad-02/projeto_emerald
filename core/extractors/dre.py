import re
import unicodedata

class DreTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        # Âncoras normalizadas para garantir o "match" na Etapa 2
        self.ancoras_grau_1 = [
            "RECEITA BRUTA", "DEDUCOES", "RECEITA LIQUIDA", "CMV", 
            "LUCRO BRUTO", "DESPESAS OPERACIONAIS", "DESPESAS COM VENDAS", 
            "DESPESA COM PESSOAL", "DESPESAS ADMINISTRATIVAS", 
            "DESPESAS TRIBUTARIAS", "DESPESAS FINANCEIRAS", 
            "RESULTADO OPERACIONAL", "PREJUIZO DO EXERCICIO", "LUCRO DO EXERCICIO"
        ]
        self.metadata = {"empresa": "Não Identificada", "ano": None}

    def _normalizar(self, texto):
        if not texto: return ""
        texto = unicodedata.normalize('NFD', texto)
        texto = "".join([c for c in texto if unicodedata.category(c) != 'Mn'])
        return texto.upper().strip()

    def _extrair_ano_robusto(self, texto):
        """Busca o ano 202X em datas ou de forma avulsa no cabeçalho."""
        # 1. Procura em frases típicas: 'Demonstração de 2023' ou 'Exercício: 2023'
        match_frase = re.search(r"(?:Resultado|Exercício|Período).*?(\b202[0-9]\b)", texto, re.IGNORECASE)
        if match_frase: return match_frase.group(1)

        # 2. Procura em datas completas DD/MM/AAAA
        match_data = re.search(r"\d{2}/\d{2}/(202[0-9])", texto)
        if match_data: return match_data.group(1)

        # 3. Fallback: Primeiro 202X encontrado no início do texto
        match_avulso = re.search(r"\b202[0-9]\b", texto[:500])
        if match_avulso: return match_avulso.group()
        
        return None

    def execute(self):
        # 1. Captura Metadados (Ano e Empresa)
        self.metadata["ano"] = self._extrair_ano_robusto(self.content)
        
        lines = self.content.splitlines()
        contas = []
        ancoras_norm = [self._normalizar(a) for a in self.ancoras_grau_1]
        indicadores_finais = {a_norm: 0.0 for a_norm in ancoras_norm}
        grupo_pai_atual = None

        for line in lines:
            linha_limpa = line.strip()
            if not linha_limpa: continue

            # Identifica Empresa no cabeçalho
            if "Empresa:" in linha_limpa:
                match_emp = re.search(r'Empresa:[,:]?\s*([^,;"]+)', linha_limpa, re.IGNORECASE)
                if match_emp: self.metadata["empresa"] = match_emp.group(1).strip().upper()

            # 2. Extração de colunas (Lida com aspas do CSV Itasul)
            colunas = re.findall(r'"([^"]*)"', linha_limpa)
            # Fallback se não houver aspas: divide por vírgulas múltiplas
            if not colunas:
                colunas = [c.strip() for c in re.split(r',+', linha_limpa) if c.strip()]

            if len(colunas) < 2: continue

            desc_original = colunas[0].strip()
            # O valor na DRE costuma ser a última coluna com números
            valores_na_linha = [c for c in colunas[1:] if re.search(r'\d', str(c))]
            if not valores_na_linha: continue
            
            valor_raw = valores_na_linha[-1]
            desc_norm = self._normalizar(desc_original)
            valor_final = self._parse_flexible_number(valor_raw)

            # 3. Mapeamento de Âncoras Grau 1 (Etapa 2 do Checklist)
            is_g1 = False
            for a_norm in ancoras_norm:
                if a_norm in desc_norm: # Busca parcial normalizada
                    indicadores_finais[a_norm] = valor_final
                    grupo_pai_atual = a_norm
                    is_g1 = True
                    break

            contas.append({
                "descricao": desc_original,
                "valor": valor_final,
                "nivel": 1 if is_g1 else 2,
                "pai": None if is_g1 else grupo_pai_atual
            })

        return {
            "metadata": self.metadata,
            "indicadores_grau_1": indicadores_finais,
            "contas": contas
        }

    def _parse_flexible_number(self, s):
        if not s or str(s).strip() in ['0.00', '0,00', '-', '']: return 0.0
        s = str(s)
        # Identifica se é negativo (parênteses ou sinal de menos)
        is_negativo = '(' in s or '-' in s
        clean = re.sub(r'[^\d,.]', '', s)
        
        # Normalização decimal
        if ',' in clean and '.' in clean:
            if clean.rfind(',') > clean.rfind('.'): clean = clean.replace('.', '').replace(',', '.')
            else: clean = clean.replace(',', '')
        else:
            clean = clean.replace(',', '.')

        try:
            val = float(clean)
            return -val if is_negativo else val
        except: return 0.0