from core.extractors.base import BaseExtractor


class _DreParser(BaseExtractor):
    INDICADORES_BASE = {
        "RECEITA BRUTA": 0.0,
        "RECEITA LIQUIDA": 0.0,
        "LUCRO BRUTO": 0.0,
        "DESPESAS OPERACIONAIS": 0.0,
        "RESULTADO OPERACIONAL": 0.0,
        "LUCRO DO EXERCICIO": 0.0,
    }

    def _extract_from_rows(self, rows):
        indicadores = dict(self.INDICADORES_BASE)
        metadata = {
            "ano": None,
            "ano_documento": None,
            "empresa": "Não Identificada",
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

            valor = 0.0
            if len(partes) > 11:
                valor = self.parse_decimal(partes[11])

            if "RECEITA BRUTA" in line_norm:
                indicadores["RECEITA BRUTA"] = valor
            elif "RECEITA" in line_norm and ("LIQUIDA" in line_norm or "QUIDA" in line_norm):
                indicadores["RECEITA LIQUIDA"] = valor
            elif "LUCRO BRUTO" in line_norm:
                indicadores["LUCRO BRUTO"] = valor
            elif "DESPESAS OPERACIONAIS" in line_norm:
                indicadores["DESPESAS OPERACIONAIS"] = valor
            elif "RESULTADO OPERACIONAL" in line_norm:
                indicadores["RESULTADO OPERACIONAL"] = valor
            elif "LUCRO" in line_norm and (
                "LIQUIDO DO EXERCICIO" in line_norm
                or "LIQUIDO DO PERIODO" in line_norm
                or "LUCRO DO EXERCICIO" in line_norm
            ):
                indicadores["LUCRO DO EXERCICIO"] = valor

        if not metadata["ano"]:
            metadata["ano"] = self.extract_year(getattr(self.file, "filename", ""))

        metadata["ano_documento"] = metadata["ano"]

        return {
            "metadata": metadata,
            "ano_referencia": metadata["ano"],
            "indicadores_grau_1": indicadores,
        }
