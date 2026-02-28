from core.extractors.balancetes.balancete_csv import BalanceteCsvExtractor
from core.extractors.balancetes.balancete_pdf import BalancetePdfExtractor
from core.extractors.balancetes.balancete_xls import BalanceteXlsExtractor
from core.extractors.balancetes.balancete_xlsx import BalanceteXlsxExtractor
from core.extractors.dre.dre_csv import DreCsvExtractor
from core.extractors.dre.dre_pdf import DrePdfExtractor
from core.extractors.dre.dre_xls import DreXlsExtractor
from core.extractors.dre.dre_xlsx import DreXlsxExtractor
from core.utils.financial_metrics import FinancialMetricsCalculator


class FinancialService:
    EXTRACTORS = {
        "dre": {
            ".csv": DreCsvExtractor,
            ".xls": DreXlsExtractor,
            ".xlsx": DreXlsxExtractor,
            ".pdf": DrePdfExtractor,
        },
        "balancete": {
            ".csv": BalanceteCsvExtractor,
            ".xls": BalanceteXlsExtractor,
            ".xlsx": BalanceteXlsxExtractor,
            ".pdf": BalancetePdfExtractor,
        },
    }

    @staticmethod
    def _identificar_tipo_documento(filename):
        import re

        nome = re.sub(r"[^A-Z0-9]", "", filename.upper())
        if "DRE" in nome or "DEMONSTRACAO" in nome:
            return "dre"
        return "balancete"

    @staticmethod
    def _selecionar_extrator(file):
        nome = file.filename or ""
        ext = "." + nome.lower().split(".")[-1] if "." in nome else ""
        tipo = FinancialService._identificar_tipo_documento(nome)
        extractor_cls = FinancialService.EXTRACTORS.get(tipo, {}).get(ext)
        return tipo, extractor_cls

    @staticmethod
    def _ordenar_anos(anos):
        return sorted(anos, key=lambda a: (0, int(a)) if str(a).isdigit() else (1, str(a)))

    @staticmethod
    def _extrair_placeholders(ano_data):
        balancete_data = (ano_data or {}).get("balancete") or {}
        dre_data = (ano_data or {}).get("dre") or {}

        resumo = balancete_data.get("resumo_grau_1", {})
        indicadores = dre_data.get("indicadores_grau_1", {})

        p_bal = {
            "ATIVO_CIRC_ATUAL": abs(float(resumo.get("Ativo Circulante", 0) or 0)),
            "ATIVO_NAO_CIRC_ATUAL": abs(float(resumo.get("Ativo Não Circulante", 0) or 0)),
            "PASS_CIRC_ATUAL": abs(float(resumo.get("Passivo Circulante", 0) or 0)),
            "PASS_NAO_CIRC_ATUAL": abs(float(resumo.get("Passivo Não Circulante", 0) or 0)),
            "PL_ATUAL": abs(float(resumo.get("Patrimônio Líquido", 0) or 0)),
        }

        p_dre = {
            "RECEITA_LIQ_ATUAL": abs(float(indicadores.get("RECEITA LIQUIDA", 0) or 0)),
            "LUCRO_LIQ_ATUAL": abs(float(indicadores.get("LUCRO DO EXERCICIO", 0) or 0)),
        }

        return p_bal, p_dre

    @staticmethod
    def _montar_tabelas(anos_ordenados, dados_por_ano):
        if not anos_ordenados:
            return [], []

        ano_atual = anos_ordenados[-1]
        ano_anterior = anos_ordenados[-2] if len(anos_ordenados) > 1 else None

        bal_atual = ((dados_por_ano.get(ano_atual, {}).get("balancete") or {}).get("resumo_grau_1", {}))
        bal_ant = ((dados_por_ano.get(ano_anterior, {}).get("balancete") or {}).get("resumo_grau_1", {})) if ano_anterior else {}

        dre_atual = ((dados_por_ano.get(ano_atual, {}).get("dre") or {}).get("indicadores_grau_1", {}))
        dre_ant = ((dados_por_ano.get(ano_anterior, {}).get("dre") or {}).get("indicadores_grau_1", {})) if ano_anterior else {}

        def montar_tabela(dic_atual, dic_ant):
            contas = sorted(set(dic_atual.keys()) | set(dic_ant.keys()))
            tabela = []
            for conta in contas:
                v_atual = abs(float(dic_atual.get(conta, 0) or 0))
                v_ant = abs(float(dic_ant.get(conta, 0) or 0))
                variacao = v_atual - v_ant
                perc = (variacao / v_ant * 100) if v_ant else 0
                if perc > 0.5:
                    status = "▲ Crescimento"
                elif perc < -0.5:
                    status = "▼ Queda"
                else:
                    status = "● Estável"

                tabela.append(
                    {
                        "conta": conta,
                        "anterior": v_ant,
                        "atual": v_atual,
                        "perc": round(perc, 2),
                        "status": status,
                    }
                )
            return tabela

        return montar_tabela(bal_atual, bal_ant), montar_tabela(dre_atual, dre_ant)

    @staticmethod
    def processar_arquivos(files):
        dados_por_ano = {}

        for file in files:
            tipo, extractor_cls = FinancialService._selecionar_extrator(file)
            if not extractor_cls:
                continue

            resultado = extractor_cls(file).execute()
            ano = str(resultado.get("metadata", {}).get("ano_documento") or resultado.get("metadata", {}).get("ano") or "Desconhecido")

            if ano not in dados_por_ano:
                dados_por_ano[ano] = {"dre": None, "balancete": None}

            resultado["ano_referencia"] = ano
            dados_por_ano[ano][tipo] = resultado

        anos_validos = [ano for ano in dados_por_ano.keys() if ano != "Desconhecido"]
        if not anos_validos:
            return {"error": "Nenhum documento com ano de referência válido foi identificado."}

        anos_ordenados = FinancialService._ordenar_anos(anos_validos)
        ano_atual = anos_ordenados[-1]
        ano_anterior = anos_ordenados[-2] if len(anos_ordenados) > 1 else None

        p_bal, p_dre = FinancialService._extrair_placeholders(dados_por_ano.get(ano_atual, {}))
        indices = FinancialMetricsCalculator.calcular_indices(p_bal, p_dre)
        comparativo_trib = FinancialService.calcular_tributacao_detalhada(
            p_dre.get("RECEITA_LIQ_ATUAL", 0), p_dre.get("LUCRO_LIQ_ATUAL", 0)
        )

        tabela_patrimonial, tabela_dre = FinancialService._montar_tabelas(anos_ordenados, dados_por_ano)

        p_bal_ant, _ = FinancialService._extrair_placeholders(dados_por_ano.get(ano_anterior, {})) if ano_anterior else ({}, {})

        graficos_data = {
            "composicao_ativo": [
                {"name": "Circulante", "value": p_bal.get("ATIVO_CIRC_ATUAL", 0)},
                {"name": "Não Circulante", "value": p_bal.get("ATIVO_NAO_CIRC_ATUAL", 0)},
            ],
            "composicao_passivo": [
                {"name": "Circulante", "value": p_bal.get("PASS_CIRC_ATUAL", 0)},
                {"name": "Não Circulante", "value": p_bal.get("PASS_NAO_CIRC_ATUAL", 0)},
                {"name": "PL Atual", "value": p_bal.get("PL_ATUAL", 0)},
            ],
            "evolucao_patrimonial": {
                "categorias": ["Ativo Total", "Passivo Total", "Patrimônio Líquido"],
                "anterior": [
                    p_bal_ant.get("ATIVO_CIRC_ATUAL", 0) + p_bal_ant.get("ATIVO_NAO_CIRC_ATUAL", 0),
                    p_bal_ant.get("PASS_CIRC_ATUAL", 0) + p_bal_ant.get("PASS_NAO_CIRC_ATUAL", 0),
                    p_bal_ant.get("PL_ATUAL", 0),
                ],
                "atual": [
                    p_bal.get("ATIVO_CIRC_ATUAL", 0) + p_bal.get("ATIVO_NAO_CIRC_ATUAL", 0),
                    p_bal.get("PASS_CIRC_ATUAL", 0) + p_bal.get("PASS_NAO_CIRC_ATUAL", 0),
                    p_bal.get("PL_ATUAL", 0),
                ],
            },
            "dre": [
                {"name": "Receita Líquida", "valor": p_dre.get("RECEITA_LIQ_ATUAL", 0)},
                {"name": "Lucro Líquido", "valor": p_dre.get("LUCRO_LIQ_ATUAL", 0)},
            ],
        }

        recomendacoes = FinancialService.gerar_recomendacoes_automaticas(indices, comparativo_trib)

        empresa = (
            dados_por_ano.get(ano_atual, {}).get("balancete", {}).get("metadata", {}).get("empresa")
            or dados_por_ano.get(ano_atual, {}).get("dre", {}).get("metadata", {}).get("empresa")
            or "Empresa não Identificada"
        )

        anos_payload = {ano: dados_por_ano[ano] for ano in anos_ordenados}

        return {
            "empresa": empresa,
            "indices": indices,
            "tabela_patrimonial": tabela_patrimonial,
            "tabela_dre": tabela_dre,
            "comparativo_tributario": comparativo_trib,
            "graficos": graficos_data,
            "recomendacoes_auto": recomendacoes,
            "anos": anos_payload,
        }

    @staticmethod
    def calcular_tributacao_detalhada(receita_anual, lucro_anual):
        """Calcula regimes tributários conforme regras de 2026"""
        if receita_anual <= 180000:
            simples = receita_anual * 0.06
        elif receita_anual <= 3600000:
            simples = (receita_anual * 0.21) - 125640
        else:
            simples = (receita_anual * 0.33) - 648000

        base_irpj = receita_anual * 0.08
        base_csll = receita_anual * 0.12
        imposto_irpj = base_irpj * 0.15 + (max(0, base_irpj - 240000) * 0.10)
        imposto_csll = base_csll * 0.09
        pis_cofins = receita_anual * (0.0065 + 0.03)
        total_presumido = imposto_irpj + imposto_csll + pis_cofins
        valor_lucro_real = round(lucro_anual * 0.34, 2) if lucro_anual > 0 else 0

        regimes = [
            {"nome": "Simples Nacional", "valor": round(simples, 2)},
            {"nome": "Lucro Presumido", "valor": round(total_presumido, 2)},
            {"nome": "Lucro Real", "valor": valor_lucro_real},
        ]

        menor = min(r["valor"] for r in regimes)
        for r in regimes:
            r["economica"] = r["valor"] == menor

        return regimes

    @staticmethod
    def gerar_recomendacoes_automaticas(indices, comparativo_trib):
        sugestoes = []
        liq = indices.get("liq_corrente", 0)
        endiv = indices.get("endiv_geral", 0)

        if liq < 1.0:
            sugestoes.append(
                {
                    "titulo": "Reestruturação de Passivo",
                    "texto": f"O índice de {liq} indica que a empresa não cobre suas obrigações imediatas. Priorizar o alongamento das dívidas de curto prazo.",
                    "urgencia": "ALTA",
                }
            )

        if endiv > 70:
            sugestoes.append(
                {
                    "titulo": "Aporte de Capital ou Desimobilização",
                    "texto": f"O endividamento de {endiv}% exige a conversão de ativos não circulantes em caixa ou aporte dos sócios para equilibrar o PL.",
                    "urgencia": "CRÍTICA",
                }
            )

        melhor_opcao = next((r for r in comparativo_trib if r["economica"]), None)
        if melhor_opcao and melhor_opcao["nome"] != "Simples Nacional":
            sugestoes.append(
                {
                    "titulo": f"Migração para {melhor_opcao['nome']}",
                    "texto": f"Adoção imediata do regime de {melhor_opcao['nome']} para reduzir a carga tributária anual.",
                    "urgencia": "ESTRATÉGICA",
                }
            )

        return sugestoes
