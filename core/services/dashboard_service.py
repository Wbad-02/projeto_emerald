import io
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class DashboardServiceError(Exception):
    pass


@dataclass
class ParsedUpload:
    tipo: str
    ano: int
    dados: Dict[str, float]
    nome_arquivo: str


class DashboardService:
    BALANCETE_CODES = {
        "ATIVO_CIRC": "1.1",
        "ATIVO_NAO_CIRC": "1.2",
        "PASS_CIRC": "2.1",
        "PASS_NAO_CIRC": "2.2",
        "PL": "2.3",
    }

    DRE_LABELS = {
        "RECEITA_BRUTA": ["receita bruta"],
        "RECEITA_LIQ": ["receita liquida", "receita líquida"],
        "LUCRO_BRUTO": ["lucro bruto"],
        "DESP_OPER": ["despesas operacionais", "despesa operacional"],
        "EBITDA": ["ebitda"],
        "LUCRO_LIQ": ["lucro liquido", "lucro líquido"],
    }

    @staticmethod
    def normalize_number(value: Any) -> float:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)) and not pd.isna(value):
            return float(value)

        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null", "-"}:
            return 0.0
        text = text.replace("R$", "").replace(" ", "")

        if "," in text and "." in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif "," in text:
            text = text.replace(".", "").replace(",", ".")

        text = re.sub(r"[^0-9\-.]", "", text)
        try:
            return float(text)
        except ValueError:
            return 0.0

    @staticmethod
    def detect_year(file_name: str, file_obj=None, forced_year: Optional[int] = None) -> int:
        if forced_year:
            return int(forced_year)

        match = re.search(r"(20\d{2})", file_name or "")
        if match:
            return int(match.group(1))

        if file_obj is not None:
            df = DashboardService._read_dataframe(file_obj, nrows=40)
            for col in df.columns:
                val = str(col)
                m = re.search(r"(20\d{2})", val)
                if m:
                    return int(m.group(1))
            for row in df.head(40).values:
                for cell in row:
                    m = re.search(r"(20\d{2})", str(cell))
                    if m:
                        return int(m.group(1))

        raise DashboardServiceError("Ano do arquivo não identificado.")

    @staticmethod
    def _read_dataframe(file_obj, nrows: Optional[int] = None) -> pd.DataFrame:
        filename = (file_obj.filename or "").lower()
        file_obj.stream.seek(0)
        content = file_obj.stream.read()
        buffer = io.BytesIO(content)

        if filename.endswith(".csv") or filename.endswith(".txt"):
            buffer.seek(0)
            try:
                return pd.read_csv(buffer, sep=None, engine="python", nrows=nrows)
            except Exception:
                buffer.seek(0)
                return pd.read_csv(buffer, sep=";", encoding="latin-1", nrows=nrows)
        if filename.endswith(".xlsx"):
            return pd.read_excel(buffer, engine="openpyxl", nrows=nrows)
        if filename.endswith(".xls"):
            return pd.read_excel(buffer, engine="xlrd", nrows=nrows)

        raise DashboardServiceError(f"Formato não suportado: {filename}")

    @classmethod
    def detect_statement_type(cls, file_obj) -> str:
        df = cls._read_dataframe(file_obj, nrows=20)
        cols = [str(c).lower() for c in df.columns]

        has_code_col = any("cod" in c for c in cols)
        sample_desc = " ".join(str(v).lower() for v in df.head(20).values.flatten())
        dre_hits = sum(1 for aliases in cls.DRE_LABELS.values() for alias in aliases if alias in sample_desc)

        if has_code_col:
            return "balancete"
        if dre_hits > 0:
            return "dre"
        return "balancete"

    @staticmethod
    def _find_col(columns: List[str], tokens: List[str]) -> Optional[str]:
        for col in columns:
            c = col.lower()
            if all(tok in c for tok in tokens):
                return col
        return None

    @staticmethod
    def _safe_div(numerator: float, denominator: float) -> float:
        if denominator == 0:
            return 0.0
        return numerator / denominator

    @classmethod
    def parse_balancete(cls, file, ano: int) -> Dict[str, float]:
        df = cls._read_dataframe(file)
        df.columns = [str(c).strip() for c in df.columns]
        cols = list(df.columns)

        code_col = cls._find_col(cols, ["cod"]) or cols[0]
        desc_col = cls._find_col(cols, ["desc"]) or cols[min(1, len(cols) - 1)]
        value_col = cls._find_col(cols, ["saldo"]) or cols[-1]

        result = {k: 0.0 for k in [*cls.BALANCETE_CODES.keys(), "ESTOQUES", "DISPONIBILIDADES"]}

        for _, row in df.iterrows():
            code = str(row.get(code_col, "")).strip()
            desc = str(row.get(desc_col, "")).lower()
            value = cls.normalize_number(row.get(value_col, 0))

            for key, prefix in cls.BALANCETE_CODES.items():
                if code.startswith(prefix):
                    result[key] += value

            if "estoque" in desc:
                result["ESTOQUES"] += value
            if any(token in desc for token in ["caixa", "banco", "equivalente", "disponibil"]):
                result["DISPONIBILIDADES"] += value

        result[f"ATIVO_TOTAL_{ano}"] = result["ATIVO_CIRC"] + result["ATIVO_NAO_CIRC"]
        result[f"PASSIVO_TOTAL_{ano}"] = result["PASS_CIRC"] + result["PASS_NAO_CIRC"] + result["PL"]
        return result

    @classmethod
    def parse_dre(cls, file, ano: int) -> Dict[str, float]:
        df = cls._read_dataframe(file)
        df.columns = [str(c).strip() for c in df.columns]
        cols = list(df.columns)

        desc_col = cls._find_col(cols, ["desc"]) or cols[0]
        value_col = cls._find_col(cols, ["valor"]) or cols[-1]

        result = {k: 0.0 for k in cls.DRE_LABELS.keys()}
        for _, row in df.iterrows():
            desc = str(row.get(desc_col, "")).lower()
            value = cls.normalize_number(row.get(value_col, 0))
            for key, aliases in cls.DRE_LABELS.items():
                if any(alias in desc for alias in aliases):
                    result[key] = value

        return result

    @staticmethod
    def _interpret_liquidez(value: float) -> Tuple[str, str]:
        if value < 1.0:
            return "crítico", "negative"
        if value < 1.5:
            return "atenção", "neutral"
        if value <= 2.0:
            return "bom", "positive"
        return "excelente", "positive"

    @staticmethod
    def _interpret_endiv(value: float) -> Tuple[str, str]:
        if value < 30:
            return "excelente", "positive"
        if value < 50:
            return "bom", "positive"
        if value <= 70:
            return "atenção", "neutral"
        return "crítico", "negative"

    @staticmethod
    def _interpret_rent(value: float, ranges: List[Tuple[float, str, str]]) -> Tuple[str, str]:
        for limit, text, css in ranges:
            if value < limit:
                return text, css
        return ranges[-1][1], ranges[-1][2]

    @classmethod
    def _build_card(cls, titulo: str, valor: float, sufixo: str, texto: str, css: str, acao: str) -> str:
        valor_fmt = f"{valor:.2f}{sufixo}"
        return (
            f'<div class="card metric-card {css}"><h4>{titulo}</h4>'
            f'<p class="valor card-default">{valor_fmt}</p>'
            f'<p class="card-hover">{valor_fmt} · {acao}</p>'
            f"<small>{texto}</small></div>"
        )

    @staticmethod
    def _build_variation(base: float, comp: float) -> Dict[str, float | str]:
        var = comp - base
        perc = 0.0 if base == 0 else (var / base) * 100
        if perc > 0.5:
            status = "▲ Crescimento"
        elif perc < -0.5:
            status = "▼ Queda"
        else:
            status = "● Estável"
        return {"base": base, "comp": comp, "var": var, "perc": perc, "status": status}


    @staticmethod
    def _status_icon(status: str) -> str:
        if "Crescimento" in status:
            return "▲"
        if "Queda" in status:
            return "▼"
        return "●"

    @classmethod
    def _render_comparison_rows(cls, comparacoes: Dict[str, Dict[str, float | str]]) -> str:
        labels = {
            "RECEITA_LIQ": "Receita Líquida",
            "LUCRO_LIQ": "Lucro Líquido",
            "ATIVO_TOTAL": "Ativo Total",
            "PASSIVO_TOTAL": "Passivo Total",
        }

        rows = []
        for key, data in comparacoes.items():
            status = str(data.get("status", "● Estável"))
            css = "positive" if "Crescimento" in status else "negative" if "Queda" in status else "neutral"
            icon = cls._status_icon(status)
            rows.append(
                "<tr class='comparison-row'>"
                f"<td>{labels.get(key, key)}</td>"
                f"<td class='text-right'>R$ {float(data.get('base', 0)):,.2f}</td>"
                f"<td class='text-right value-highlight {css}'>R$ {float(data.get('comp', 0)):,.2f}"
                f"<span class='variation-badge {css}'>{icon} {float(data.get('perc', 0)):.2f}%</span>"
                "</td>"
                f"<td class='text-center status-pill {css}'>{status}</td>"
                "</tr>"
            )
        return "".join(rows)


    @staticmethod
    def _format_currency(value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @classmethod
    def _render_overlap_columns(
        cls,
        titulo: str,
        ano_base: int,
        ano_comp: int,
        items: List[Tuple[str, float, float]],
    ) -> str:
        normalized = [(label, max(0.0, float(base)), max(0.0, float(comp))) for label, base, comp in items]
        max_value = max((max(base, comp) for _, base, comp in normalized), default=0.0)
        columns = []
        for label, base, comp in normalized:
            base_h = 0 if max_value == 0 else (base / max_value) * 100
            comp_h = 0 if max_value == 0 else (comp / max_value) * 100
            columns.append(
                "<div class='col-item'>"
                f"<div class='col-values'><small>{cls._format_currency(base)}</small><small>{cls._format_currency(comp)}</small></div>"
                "<div class='col-wrap'>"
                f"<span class='col-base' style='height:{base_h:.2f}%'></span>"
                f"<span class='col-comp' style='height:{comp_h:.2f}%'></span>"
                "</div>"
                f"<div class='col-label'>{label}</div>"
                "</div>"
            )

        return (
            "<div class='chart-card'>"
            f"<h4>{titulo}</h4>"
            f"<div class='chart-legend'><span><i class='legend-box base'></i>{ano_base}</span>"
            f"<span><i class='legend-box comp'></i>{ano_comp}</span></div>"
            f"<div class='col-chart'>{''.join(columns)}</div>"
            "</div>"
        )

    @staticmethod
    def _tributos(receita_bruta: float, lucro_liq: float) -> List[Dict[str, Any]]:
        simples = receita_bruta * 0.06
        base_pres = receita_bruta * 0.08
        irpj = base_pres * 0.15 + max(0.0, base_pres - 240000) * 0.10
        csll = receita_bruta * 0.12 * 0.09
        pis_cofins_pres = receita_bruta * (0.0065 + 0.03)
        presumido = irpj + csll + pis_cofins_pres

        real_irpj = max(0.0, lucro_liq) * 0.15
        real_csll = max(0.0, lucro_liq) * 0.09
        real_piscofins = receita_bruta * (0.0165 + 0.076)
        real = real_irpj + real_csll + real_piscofins

        return [
            {"nome": "Simples Nacional (estimativa)", "valor": round(simples, 2)},
            {"nome": "Lucro Presumido (estimativa)", "valor": round(presumido, 2)},
            {"nome": "Lucro Real (estimativa)", "valor": round(real, 2)},
        ]

    @classmethod
    def compute_metrics(cls, dados_por_ano: Dict[int, Dict[str, Dict[str, float]]]) -> Dict[str, Any]:
        warnings: List[str] = []
        anos = sorted(dados_por_ano.keys())
        if not anos:
            raise DashboardServiceError("Nenhum dado processável enviado.")

        placeholders: Dict[str, Any] = {}
        for ano in anos:
            bal = dados_por_ano[ano].get("balancete", {})
            dre = dados_por_ano[ano].get("dre", {})
            for k, v in bal.items():
                key_name = k if k.endswith(f"_{ano}") else f"{k}_{ano}"
                placeholders[key_name] = v
            for k, v in dre.items():
                placeholders[f"{k}_{ano}"] = v

        ano_comp = anos[-1]
        ano_base = anos[-2] if len(anos) > 1 else anos[-1]
        placeholders["ANO_BASE"] = ano_base
        placeholders["ANO_COMPARADO"] = ano_comp

        comparacoes = {}
        for metric in ["RECEITA_LIQ", "LUCRO_LIQ", "ATIVO_TOTAL", "PASSIVO_TOTAL"]:
            base = placeholders.get(f"{metric}_{ano_base}", 0.0)
            comp = placeholders.get(f"{metric}_{ano_comp}", 0.0)
            comparacoes[metric] = cls._build_variation(base, comp)

        bal_rec = dados_por_ano[ano_comp].get("balancete", {})
        dre_rec = dados_por_ano[ano_comp].get("dre", {})

        estoques = bal_rec.get("ESTOQUES", 0.0)
        if estoques == 0:
            warnings.append("Estoques não localizados; usado valor 0.")

        disponibilidades = bal_rec.get("DISPONIBILIDADES", 0.0)
        if disponibilidades == 0:
            warnings.append("Disponibilidades não localizadas; usado valor 0.")

        ativo_circ = bal_rec.get("ATIVO_CIRC", 0.0)
        passivo_circ = bal_rec.get("PASS_CIRC", 0.0)
        pl = bal_rec.get("PL", 0.0)
        ativo_total = bal_rec.get(f"ATIVO_TOTAL_{ano_comp}", ativo_circ + bal_rec.get("ATIVO_NAO_CIRC", 0.0))
        passivo_total = bal_rec.get(f"PASSIVO_TOTAL_{ano_comp}", passivo_circ + bal_rec.get("PASS_NAO_CIRC", 0.0) + pl)
        lucro_liq = dre_rec.get("LUCRO_LIQ", 0.0)
        receita_liq = dre_rec.get("RECEITA_LIQ", 0.0)

        liq_corr = cls._safe_div(ativo_circ, passivo_circ)
        liq_seca = cls._safe_div(ativo_circ - estoques, passivo_circ)
        liq_imed = cls._safe_div(disponibilidades, passivo_circ)
        endiv_geral = cls._safe_div(passivo_total, ativo_total) * 100
        margem_liq = cls._safe_div(lucro_liq, receita_liq) * 100
        roe = cls._safe_div(lucro_liq, pl) * 100
        roa = cls._safe_div(lucro_liq, ativo_total) * 100

        liq_txt, liq_css = cls._interpret_liquidez(liq_corr)
        end_txt, end_css = cls._interpret_endiv(endiv_geral)
        m_txt, m_css = cls._interpret_rent(margem_liq, [(0, "prejuízo", "negative"), (5, "baixa", "neutral"), (10, "adequada", "neutral"), (20, "boa", "positive"), (10**9, "excelente", "positive")])
        roe_txt, roe_css = cls._interpret_rent(roe, [(0, "prejuízo", "negative"), (10, "baixo", "neutral"), (15, "adequado", "neutral"), (25, "bom", "positive"), (10**9, "excelente", "positive")])

        liq_acao = "reduzir passivos de curto prazo e reforçar caixa" if liq_corr < 1 else "manter capital de giro e revisar prazos de recebimento"
        seca_acao = "acelerar giro de estoques e renegociar dívidas de curto prazo"
        imed_acao = "reservar caixa mínimo e controlar saídas não essenciais"
        end_acao = "reduzir dependência de capital de terceiros e alongar dívidas" if endiv_geral > 70 else "manter disciplina no nível de alavancagem"
        margem_acao = "rever custos e despesas operacionais para recuperar margem" if margem_liq < 5 else "preservar eficiência operacional e política de preços"
        roe_acao = "melhorar resultado líquido com foco em rentabilidade do capital próprio"
        roa_acao = "otimizar uso dos ativos para gerar mais retorno operacional"

        cards_liq = "".join([
            cls._build_card("Liquidez Corrente", liq_corr, "", f"Nível {liq_txt}", liq_css, liq_acao),
            cls._build_card("Liquidez Seca", liq_seca, "", "Sem estoques", "neutral", seca_acao),
            cls._build_card("Liquidez Imediata", liq_imed, "", "Disponibilidades", "neutral", imed_acao),
        ])
        cards_end = cls._build_card("Endividamento Geral", endiv_geral, "%", f"Situação {end_txt}", end_css, end_acao)
        cards_rent = "".join([
            cls._build_card("Margem Líquida", margem_liq, "%", m_txt, m_css, margem_acao),
            cls._build_card("ROE", roe, "%", roe_txt, roe_css, roe_acao),
            cls._build_card("ROA", roa, "%", "Retorno sobre ativos", "neutral", roa_acao),
        ])

        positivos: List[str] = []
        atencao: List[str] = []
        if comparacoes["RECEITA_LIQ"]["perc"] > 0.5:
            positivos.append("Receita líquida apresentou crescimento no período comparado.")
        if comparacoes["LUCRO_LIQ"]["perc"] > 0.5:
            positivos.append("Lucro líquido evoluiu de forma positiva.")
        if liq_corr < 1:
            atencao.append("Liquidez corrente abaixo de 1 indica risco de caixa no curto prazo.")
        if endiv_geral > 70:
            atencao.append("Endividamento geral acima de 70% exige revisão da estrutura de capital.")
        if margem_liq < 0:
            atencao.append("Margem líquida negativa indica operação com prejuízo.")

        if not positivos:
            positivos.append("Estrutura de dados processada para comparação anual crescente.")
        if not atencao:
            atencao.append("Monitorar custos e capital de giro para sustentar crescimento.")

        receita_bruta_rec = dre_rec.get("RECEITA_BRUTA", 0.0)
        regimes = cls._tributos(receita_bruta_rec, lucro_liq)
        menor = min(r["valor"] for r in regimes) if regimes else 0
        regime_recomendado = "Não identificado"
        for r in regimes:
            r["economica"] = r["valor"] == menor
            if r["economica"]:
                regime_recomendado = r["nome"]

        placeholders.update(
            {
                "CARDS_LIQUIDEZ": cards_liq,
                "CARDS_ENDIVIDAMENTO": cards_end,
                "CARDS_RENTABILIDADE": cards_rent,
                "PONTOS_POSITIVOS_ITEMS": "".join(f"<li>{i}</li>" for i in positivos),
                "PONTOS_ATENCAO_ITEMS": "".join(f"<li>{i}</li>" for i in atencao),
                "CARDS_REGIMES": "".join(
                    f"<div class='card {'positive' if r['economica'] else 'neutral'} regime-card'><h4>{r['nome']}</h4><p class='valor'>R$ {r['valor']:,.2f}</p><small>{'Recomendado' if r['economica'] else 'Comparativo estimado'}</small></div>"
                    for r in regimes
                ),
                "REGIME_RECOMENDADO": regime_recomendado,
                "BASE_TRIBUTARIA": f"Ano {ano_comp} · Receita Bruta {cls._format_currency(receita_bruta_rec)}",
                "GRAFICO_REGIMES": json.dumps(regimes),
                "ANO_RECENTE": ano_comp,
                "RECEITA_LIQ_RECENTE": receita_liq,
                "LUCRO_LIQ_RECENTE": lucro_liq,
                "COMPARACOES": comparacoes,
                "COMPARACAO_ROWS": cls._render_comparison_rows(comparacoes),
                "GRAFICO_DRE": cls._render_overlap_columns(
                    "Comparativo DRE: ano base vs comparado",
                    ano_base,
                    ano_comp,
                    [
                        (
                            "Receita Líquida",
                            placeholders.get(f"RECEITA_LIQ_{ano_base}", 0.0),
                            receita_liq,
                        ),
                        (
                            "Lucro Líquido",
                            placeholders.get(f"LUCRO_LIQ_{ano_base}", 0.0),
                            lucro_liq,
                        ),
                        (
                            "Receita Bruta",
                            placeholders.get(f"RECEITA_BRUTA_{ano_base}", 0.0),
                            dre_rec.get("RECEITA_BRUTA", 0.0),
                        ),
                    ],
                ),
                "GRAFICO_BALANCO": cls._render_overlap_columns(
                    "Comparativo Balanço: ano base vs comparado",
                    ano_base,
                    ano_comp,
                    [
                        (
                            "Ativo Total",
                            placeholders.get(f"ATIVO_TOTAL_{ano_base}", 0.0),
                            ativo_total,
                        ),
                        (
                            "Passivo Total",
                            placeholders.get(f"PASSIVO_TOTAL_{ano_base}", 0.0),
                            passivo_total,
                        ),
                        (
                            "Patrimônio Líquido",
                            placeholders.get(f"PL_{ano_base}", 0.0),
                            pl,
                        ),
                    ],
                ),
                "warnings": warnings,
            }
        )
        return placeholders

    @staticmethod
    def render_template(placeholders: Dict[str, Any]) -> str:
        html = """
        <html><head><meta charset='utf-8'><title>Dashboard Financeiro</title>
        <style>
        body{font-family:Arial,sans-serif;padding:24px;background:#f8fafc;color:#0f172a}
        .panel{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:16px}
        .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
        .grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
        .card{border:1px solid #ddd;border-radius:10px;padding:12px}
        .regime-card{transition:transform .2s ease,box-shadow .2s ease}
        .regime-card:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(2,6,23,.12)}
        .positive{background:#e8fff2;color:#0f5132}
        .neutral{background:#f5f7fa;color:#475569}
        .negative{background:#ffecec;color:#991b1b}
        .valor{font-size:22px;font-weight:700}
        .metric-card{position:relative;min-height:120px;transition:transform .2s ease,box-shadow .2s ease}
        .metric-card:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(2,6,23,.12)}
        .card-default{opacity:1;transition:opacity .2s ease}
        .card-hover{position:absolute;left:12px;right:12px;top:46px;font-size:13px;line-height:1.35;font-weight:600;opacity:0;transition:opacity .2s ease}
        .metric-card:hover .card-default{opacity:0}
        .metric-card:hover .card-hover{opacity:1}
        ul{margin-top:0}
        .comparison-table{width:100%;border-collapse:collapse;margin:8px 0}
        .comparison-table th,.comparison-table td{padding:10px;border-bottom:1px solid #e2e8f0}
        .comparison-row{transition:background .2s ease}.comparison-row:hover{background:#f8fafc}
        .text-right{text-align:right}.text-center{text-align:center}
        .value-highlight{position:relative;font-weight:700;transition:transform .2s ease,box-shadow .2s ease;padding-right:72px}
        .comparison-row:hover .value-highlight{transform:scale(1.04);box-shadow:0 6px 14px rgba(15,23,42,.12);border-radius:8px}
        .variation-badge{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px;opacity:0;transition:opacity .2s ease}
        .comparison-row:hover .variation-badge{opacity:1}.status-pill{font-size:11px;font-weight:700;padding:4px 8px;border-radius:999px}
        .chart-card{border:1px solid #e2e8f0;border-radius:10px;padding:12px;background:#fff}
        .chart-card h4{margin:0 0 10px 0}
        .chart-legend{display:flex;gap:14px;font-size:12px;margin-bottom:8px;color:#334155}
        .legend-box{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:5px}
        .legend-box.base{background:rgba(71,85,105,.35);border:1px solid rgba(71,85,105,.7)}
        .legend-box.comp{background:rgba(16,185,129,.45);border:1px solid rgba(5,150,105,.9)}
        .col-chart{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;align-items:end;height:240px}
        .col-item{display:flex;flex-direction:column;gap:6px}
        .col-values{display:flex;justify-content:space-between;font-size:10px;color:#475569}
        .col-wrap{position:relative;height:180px;background:#f1f5f9;border-radius:8px;overflow:hidden;display:flex;align-items:flex-end;justify-content:center}
        .col-base,.col-comp{position:absolute;bottom:0;border-radius:6px 6px 0 0;transition:height .25s ease}
        .col-base{width:54%;background:rgba(71,85,105,.35);border:1px solid rgba(71,85,105,.7)}
        .col-comp{width:36%;background:rgba(16,185,129,.45);border:1px solid rgba(5,150,105,.9)}
        .col-label{font-size:12px;text-align:center;color:#334155;font-weight:600}
        @media (max-width: 980px){.grid,.grid-2{grid-template-columns:1fr}}
        @media print {
          @page { size: A4; margin: 12mm; }
          html, body { background: #ffffff !important; }
          body { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; padding: 0; }
          .panel { page-break-inside: avoid; box-shadow: none !important; }
          .metric-card:hover .card-default{opacity:1}
          .metric-card .card-hover{display:none}
        }
        </style>
        </head><body>
        <div class='panel'>
          <h1>Dashboard Financeiro - Ano {{ANO_RECENTE}}</h1>
          <p>Estrutura integrada por ano: base <strong>{{ANO_BASE}}</strong> vs comparado <strong>{{ANO_COMPARADO}}</strong>.</p>
        </div>

        <div class='panel'>
          <h2>Índices de Liquidez</h2><div class='grid'>{{CARDS_LIQUIDEZ}}</div>
        </div>

        <div class='panel'>
          <h2>Índice de Endividamento</h2><div class='grid'>{{CARDS_ENDIVIDAMENTO}}</div>
        </div>

        <div class='panel'>
          <h2>Rentabilidade</h2><div class='grid'>{{CARDS_RENTABILIDADE}}</div>
        </div>

        <div class='panel'>
          <h2>Comparação anual consolidada</h2>
          <table class='comparison-table'>
            <thead><tr><th>Conta</th><th class='text-right'>Ano Base</th><th class='text-right'>Ano Comparado</th><th class='text-center'>Status</th></tr></thead>
            <tbody>{{COMPARACAO_ROWS}}</tbody>
          </table>
        </div>

        <div class='panel'>
          <h2>Gráficos gerenciais</h2>
          <div class='grid-2'>{{GRAFICO_DRE}}{{GRAFICO_BALANCO}}</div>
        </div>

        <div class='panel grid-2'>
          <div><h2>Pontos positivos</h2><ul>{{PONTOS_POSITIVOS_ITEMS}}</ul></div>
          <div><h2>Pontos de atenção</h2><ul>{{PONTOS_ATENCAO_ITEMS}}</ul></div>
        </div>

        <div class='panel'>
          <h2>Regimes tributários (estimativas)</h2>
          <p><strong>Regime recomendado:</strong> {{REGIME_RECOMENDADO}} <small>({{BASE_TRIBUTARIA}})</small></p>
          <div class='grid'>{{CARDS_REGIMES}}</div>
        </div>
        <script>window.__REGIMES__={{GRAFICO_REGIMES}};</script>
        </body></html>
        """
        rendered = html
        for key, value in placeholders.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        rendered = re.sub(r"\{\{[A-Z0-9_]+\}\}", "0", rendered)
        return rendered

    @classmethod
    def generate_dashboard(cls, files, year_map: Dict[str, int]) -> Dict[str, Any]:
        dados_por_ano: Dict[int, Dict[str, Dict[str, float]]] = {}
        for file in files:
            name = file.filename or ""
            ano = cls.detect_year(name, file, year_map.get(name))
            lower_name = name.lower()
            if "dre" in lower_name:
                tipo = "dre"
            elif "balancete" in lower_name or "balanco" in lower_name:
                tipo = "balancete"
            else:
                tipo = cls.detect_statement_type(file)
            parsed = cls.parse_dre(file, ano) if tipo == "dre" else cls.parse_balancete(file, ano)
            dados_por_ano.setdefault(ano, {}).setdefault(tipo, {}).update(parsed)

        for ano in list(dados_por_ano.keys()):
            dados_por_ano[ano].setdefault("dre", {})
            dados_por_ano[ano].setdefault("balancete", {})

        placeholders = cls.compute_metrics(dados_por_ano)
        html = cls.render_template(placeholders)
        anos = sorted(dados_por_ano.keys())
        return {
            "html": html,
            "placeholders": placeholders,
            "anos_detectados": anos,
            "warnings": placeholders.get("warnings", []),
        }
