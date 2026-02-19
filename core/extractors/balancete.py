import re
import csv
from io import StringIO


class BalanceteTxtExtractor:

    def __init__(self, text_content):
        self.content = text_content
        self.resumo_grau_1 = {}
        self.contas = []
        self.metadata = {
            "empresa": "Não Identificada",
            "ano": None
        }

    # ==========================================================
    # METADADOS
    # ==========================================================

    def _extrair_ano_robusto(self, texto):
        """Busca o ano em múltiplos formatos possíveis."""
        match_periodo = re.search(r"Período:.*?(\b202\d\b)", texto, re.IGNORECASE)
        if match_periodo:
            return match_periodo.group(1)

        match_data = re.search(r"\d{2}/\d{2}/(202\d)", texto)
        if match_data:
            return match_data.group(1)

        match_avulso = re.search(r"\b202\d\b", texto[:1000])
        if match_avulso:
            return match_avulso.group()

        return None

    def _extrair_empresa(self, line):
        match = re.search(r'Empresa:[,:]?\s*([^,;"]+)', line, re.IGNORECASE)
        if match:
            return match.group(1).strip().upper()
        return None

    # ==========================================================
    # LEITURA SEGURA DE COLUNAS
    # ==========================================================

    def _parse_csv_line(self, line):
        """
        Lê linha usando csv para evitar bugs com aspas,
        vírgulas ou ponto e vírgula.
        """
        try:
            # Detecta delimitador automaticamente
            delimiter = ';' if line.count(';') > line.count(',') else ','
            reader = csv.reader(StringIO(line), delimiter=delimiter, quotechar='"')
            return next(reader, [])
        except Exception:
            return []

    # ==========================================================
    # NORMALIZAÇÃO NUMÉRICA ROBUSTA
    # ==========================================================

    def _normalize_number(self, s):
        if not s:
            return 0.0

        s = str(s).strip()

        if s in ['', '0', '0.00', '0,00', '-']:
            return 0.0

        # Detecta negativo por parênteses
        negative = '(' in s and ')' in s

        # Remove tudo que não for número ou separador
        s = re.sub(r'[^\d,.\-]', '', s)

        # Se tiver vírgula e ponto
        if ',' in s and '.' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        else:
            # Apenas vírgula -> padrão BR
            if ',' in s:
                s = s.replace('.', '').replace(',', '.')
            # Apenas ponto -> padrão US
            else:
                s = s.replace(',', '')

        try:
            value = float(s)
            return -abs(value) if negative else value
        except ValueError:
            return 0.0

    # ==========================================================
    # REGRA CONTÁBIL DE NATUREZA
    # ==========================================================

    def _aplicar_natureza(self, valor, codigo, raw_string):
        """
        Aplica natureza contábil com base no código da conta.
        """

        raw_string = str(raw_string).strip().lower()

        # Detecta crédito apenas se for isolado
        is_credito = bool(re.search(r'\bC\b', raw_string))

        valor = abs(valor)

        # ATIVO (devedor)
        if codigo.startswith('1'):
            return -valor if is_credito else valor

        # PASSIVO / PL (credor)
        if codigo.startswith('2'):
            return valor if is_credito else -valor

        # RECEITAS (credor)
        if codigo.startswith('6'):
            return valor if is_credito else -valor

        return valor

    # ==========================================================
    # PROCESSAMENTO PRINCIPAL
    # ==========================================================

    def execute(self):

        if not self.metadata["ano"]:
            self.metadata["ano"] = self._extrair_ano_robusto(self.content[:1000])

        lines = self.content.splitlines()

        for line in lines:

            upper_line = line.upper()

            # Ignora cabeçalhos
            if any(key in upper_line for key in [
                "EMPRESA:", "C.N.P.J.:", "CÓDIGO", "FOLHA:", "BALANCETE"
            ]):
                empresa = self._extrair_empresa(line)
                if empresa:
                    self.metadata["empresa"] = empresa
                continue

            colunas = self._parse_csv_line(line)

            if len(colunas) < 14:
                continue

            classificacao = colunas[1].strip()

            if not classificacao or not re.match(r'^\d+(\.\d+)*$', classificacao):
                continue

            descricao = colunas[3].strip().upper()

            # Saldo Atual (coluna 13)
            valor_raw = colunas[13]
            valor_numerico = self._normalize_number(valor_raw)

            # Regra especial encerramento (contas 5, 6 e 7 zeradas)
            if classificacao.startswith(('5', '6', '7')) and valor_numerico == 0:
                if classificacao.startswith('6'):
                    valor_raw = colunas[11]
                else:
                    valor_raw = colunas[9]

                valor_numerico = self._normalize_number(valor_raw)

            # Aplica natureza
            valor_final = self._aplicar_natureza(
                valor_numerico,
                classificacao,
                valor_raw
            )

            nivel = classificacao.count('.') + 1

            conta_obj = {
                "classificacao": classificacao,
                "descricao": descricao,
                "valor": valor_final,
                "nivel": nivel
            }

            self.contas.append(conta_obj)

            if nivel <= 3:
                self.resumo_grau_1[classificacao] = {
                    "nome": descricao,
                    "valor": valor_final
                }

        return {
            "metadata": self.metadata,
            "resumo_grau_1": self.resumo_grau_1,
            "contas": self.contas
        }
