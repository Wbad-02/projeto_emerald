from core.extractors.base import BaseExtractor


class _BalanceteParser(BaseExtractor):
    MAPA_SISTEMA = {
        "1": "Ativo Total",
        "1.1": "Ativo Circulante",
        "1.2": "Ativo Não Circulante",
        "2": "Passivo Total",
        "2.1": "Passivo Circulante",
        "2.2": "Passivo Não Circulante",
        "2.3": "Patrimônio Líquido",
        "1.1.01": "Disponibilidades",
        "1.1.02.04": "Estoque",
    }

    def _parse_balance_value(self, raw_value, classificacao):
        if raw_value is None:
            return 0.0

        raw = str(raw_value).strip().lower()
        value = abs(self.parse_decimal(raw))

        if value == 0:
            return 0.0

        is_debito = raw.endswith("d")
        is_credito = raw.endswith("c")

        if classificacao.startswith("2"):
            if is_credito:
                return value
            if is_debito:
                return -value
            return value

        if is_debito:
            return value
        if is_credito:
            return -value
        return value

    def _extract_from_rows(self, rows):
        resumo_grau_1 = {}
        metadata = {
            "empresa": "Não Identificada",
            "ano": None,
            "ano_documento": None,
            "cnpj": "Não Identificado",
        }

        for partes in rows:
            if not partes:
                continue

            line = " ".join(str(p) for p in partes)
            line_norm = self.normalize(line)

            if "EMPRESA:" in line_norm and metadata["empresa"] == "Não Identificada":
                for campo in partes:
                    valor = str(campo).strip()
                    if len(valor) > 5 and "EMPRESA" not in self.normalize(valor):
                        metadata["empresa"] = valor.upper()
                        break

            if "C.N.P.J" in line_norm and metadata["cnpj"] == "Não Identificado":
                import re

                match_cnpj = re.search(r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", line)
                if match_cnpj:
                    metadata["cnpj"] = match_cnpj.group(1)

            if not metadata["ano"]:
                metadata["ano"] = self.extract_year(line_norm)

            if len(partes) >= 14:
                classificacao = str(partes[1]).strip()
                if classificacao in self.MAPA_SISTEMA:
                    valor = self._parse_balance_value(partes[13], classificacao)
                    resumo_grau_1[self.MAPA_SISTEMA[classificacao]] = valor

        if not metadata["ano"]:
            metadata["ano"] = self.extract_year(getattr(self.file, "filename", ""))

        metadata["ano_documento"] = metadata["ano"]

        return {
            "metadata": metadata,
            "ano_referencia": metadata["ano"],
            "resumo_grau_1": resumo_grau_1,
        }
