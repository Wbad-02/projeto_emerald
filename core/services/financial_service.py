from core.extractors.balancetes.balancete_csv import BalanceteCsvExtractor
from core.extractors.balancetes.balancete_pdf import BalancetePdfExtractor
from core.extractors.balancetes.balancete_xls import BalanceteXlsExtractor
from core.extractors.balancetes.balancete_xlsx import BalanceteXlsxExtractor
from core.extractors.dre.dre_csv import DreCsvExtractor
from core.extractors.dre.dre_pdf import DrePdfExtractor
from core.extractors.dre.dre_xls import DreXlsExtractor
from core.extractors.dre.dre_xlsx import DreXlsxExtractor
from core.utils.calculator_balancete import FinancialCalculator
from core.utils.calculator_dre import DreCalculator
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
    def processar_arquivos(files):
        dados_por_ano = {}

        for file in files:
            tipo, extractor_cls = FinancialService._selecionar_extrator(file)
            if not extractor_cls:
                continue

            extrator = extractor_cls(file)

            resultado = extrator.execute()
            ano = str(resultado['metadata'].get('ano_documento') or resultado['metadata'].get('ano') or 'Desconhecido')
            if ano not in dados_por_ano:
                dados_por_ano[ano] = {"dre": None, "balancete": None}
            resultado["ano_referencia"] = ano
            dados_por_ano[ano][tipo] = resultado

        # Filtro de anos válidos (Necessita DRE + Balancete)
        dados_validos = {ano: d for ano, d in dados_por_ano.items() 
                        if ano != 'Desconhecido' and d["dre"] and d["balancete"]}
        
        if len(dados_validos) < 2:
            return {"error": "Dados insuficientes. Envie DRE e Balancete de pelo menos 2 anos."}

        # Processamento base para tabelas
        rel_patrimonial = FinancialCalculator.processar_dashboard(dados_validos)
        rel_dre = DreCalculator.processar_dre(dados_validos)

        # Captura dinâmica de placeholders
        p_dre = rel_dre.get("placeholders") or rel_dre.get("data", {}).get("placeholders", {})
        p_bal = rel_patrimonial.get("placeholders") or rel_patrimonial.get("data", {}).get("placeholders", {})
        
        rl_atual = p_dre.get("RECEITA_LIQ_ATUAL", 0)
        ll_atual = p_dre.get("LUCRO_LIQ_ATUAL", 0)

        # Cálculos de Índices e Tributação
        novos_indices = FinancialMetricsCalculator.calcular_indices(p_bal, p_dre)
        comparativo_trib = FinancialService.calcular_tributacao_detalhada(rl_atual, ll_atual)

        # ETAPA 5: PREPARAÇÃO DINÂMICA PARA GRÁFICOS
        at_ant = p_bal.get("ATIVO_CIRC_ANT", 0) + p_bal.get("ATIVO_NAO_CIRC_ANT", 0)
        at_atu = p_bal.get("ATIVO_CIRC_ATUAL", 0) + p_bal.get("ATIVO_NAO_CIRC_ATUAL", 0)
        pt_ant = p_bal.get("PASS_CIRC_ANT", 0) + p_bal.get("PASS_NAO_CIRC_ANT", 0)
        pt_atu = p_bal.get("PASS_CIRC_ATUAL", 0) + p_bal.get("PASS_NAO_CIRC_ATUAL", 0)

        graficos_data = {
            "composicao_ativo": [
                {"name": "Circulante", "value": p_bal.get("ATIVO_CIRC_ATUAL", 0)},
                {"name": "Não Circulante", "value": p_bal.get("ATIVO_NAO_CIRC_ATUAL", 0)}
            ],
            "composicao_passivo": [
                {"name": "Circulante", "value": p_bal.get("PASS_CIRC_ATUAL", 0)},
                {"name": "Não Circulante", "value": p_bal.get("PASS_NAO_CIRC_ATUAL", 0)},
                {"name": "PL Atual", "value": p_bal.get("PL_ATUAL", 0)}
            ],
            "evolucao_patrimonial": {
                "categorias": ["Ativo Total", "Passivo Total", "Patrimônio Líquido"],
                "anterior": [at_ant, pt_ant, p_bal.get("PL_ANT", 0)],
                "atual": [at_atu, pt_atu, p_bal.get("PL_ATUAL", 0)]
            },
            "dre": [
                {"name": "Receita Bruta", "valor": p_dre.get("RECEITA_BRUTA_ATUAL", 0)},
                {"name": "Receita Líquida", "valor": rl_atual},
                {"name": "Lucro Líquido", "valor": ll_atual}
            ]
        }

        # ETAPA 8: GERAÇÃO DE RECOMENDAÇÕES AUTOMÁTICAS
        recomendacoes = FinancialService.gerar_recomendacoes_automaticas(novos_indices, comparativo_trib)

        return {
            "empresa": rel_patrimonial.get("empresa", "Empresa não Identificada"),
            "indices": novos_indices, 
            "tabela_patrimonial": rel_patrimonial.get("tabela_patrimonial", []),
            "tabela_dre": rel_dre.get("tabela", []),
            "comparativo_tributario": comparativo_trib,
            "graficos": graficos_data,
            "recomendacoes_auto": recomendacoes,
            "anos": dados_validos
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
            {"nome": "Lucro Real", "valor": valor_lucro_real}
        ]
        
        menor = min(r["valor"] for r in regimes)
        for r in regimes: r["economica"] = (r["valor"] == menor)
            
        return regimes

    @staticmethod
    def gerar_recomendacoes_automaticas(indices, comparativo_trib):
        sugestoes = []
        liq = indices.get('liq_corrente', 0)
        endiv = indices.get('endiv_geral', 0)

        if liq < 1.0:
            sugestoes.append({
                "titulo": "Reestruturação de Passivo",
                "texto": f"O índice de {liq} indica que a empresa não cobre suas obrigações imediatas. Priorizar o alongamento das dívidas de curto prazo.",
                "urgencia": "ALTA"
            })

        if endiv > 70:
            sugestoes.append({
                "titulo": "Aporte de Capital ou Desimobilização",
                "texto": f"O endividamento de {endiv}% exige a conversão de ativos não circulantes em caixa ou aporte dos sócios para equilibrar o PL.",
                "urgencia": "CRÍTICA"
            })

        melhor_opcao = next((r for r in comparativo_trib if r['economica']), None)
        if melhor_opcao and melhor_opcao['nome'] != 'Simples Nacional':
            sugestoes.append({
                "titulo": f"Migração para {melhor_opcao['nome']}",
                "texto": f"Adoção imediata do regime de {melhor_opcao['nome']} para reduzir a carga tributária anual.",
                "urgencia": "ESTRATÉGICA"
            })

        return sugestoes
