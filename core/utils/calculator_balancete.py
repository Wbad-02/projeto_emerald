class FinancialCalculator:
    @staticmethod
    def processar_dashboard(dados_por_ano):
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: return None

        ano_ant, ano_atu = anos[0], anos[1]
        
        # Acesso aos dados brutos extraídos
        bal_ant_raw = dados_por_ano[ano_ant]["balancete"].get("resumo_grau_1", {})
        bal_atu_raw = dados_por_ano[ano_atu]["balancete"].get("resumo_grau_1", {})
        dre_atu_raw = dados_por_ano[ano_atu]["dre"].get("indicadores_grau_1", {})

        # 1. Mapeamento Ampliado (Incluindo variáveis para os novos índices)
        mapeamento = {
            "ATIVO_CIRC": "Ativo Circulante",
            "ATIVO_NAO_CIRC": "Ativo Não Circulante",
            "PASS_CIRC": "Passivo Circulante",
            "PASS_NAO_CIRC": "Passivo Não Circulante",
            "PL": "Patrimônio Líquido",
            "ESTOQUE": "Estoque",
            "DISPONIBILIDADES": "Disponibilidades"
        }

        placeholders = {}
        tabela_patrimonial = []

        # 2. Processamento das variações patrimoniais com tratamento de sinal
        for short_key, bal_label in mapeamento.items():
            # v_ant e v_atu agora usam abs() para garantir que PC e PL funcionem nos índices
            v_ant = abs(float(bal_ant_raw.get(bal_label, 0.0)))
            v_atu = abs(float(bal_atu_raw.get(bal_label, 0.0)))
            
            var = v_atu - v_ant
            perc = (var / v_ant * 100) if v_ant != 0 else 0.0
            status_str = "▲ CRESCIMENTO" if perc > 0.5 else "▼ QUEDA" if perc < -0.5 else "● ESTÁVEL"

            placeholders.update({
                f"{short_key}_ANT": v_ant,
                f"{short_key}_ATUAL": v_atu,
                f"{short_key}_PERC": round(perc, 2),
                f"{short_key}_STATUS": status_str
            })

            # Adiciona apenas as contas principais na tabela comparativa (Etapa 4)
            if short_key not in ["ESTOQUE", "DISPONIBILIDADES"]:
                tabela_patrimonial.append({
                    "conta": bal_label,
                    "anterior": v_ant,
                    "atual": v_atu,
                    "perc": round(perc, 2),
                    "status": status_str
                })

        # 3. Totais para Gráficos e Índices (Etapa 3)
        at_atu = placeholders["ATIVO_CIRC_ATUAL"] + placeholders["ATIVO_NAO_CIRC_ATUAL"]
        
        # 4. Extração de valores da DRE
        lucro_liq = abs(float(dre_atu_raw.get("LUCRO DO EXERCICIO", 0.0) or dre_atu_raw.get("LUCRO LIQUIDO", 0.0)))
        receita_liq = abs(float(dre_atu_raw.get("RECEITA LIQUIDA", 0.0)))

        # 5. Cálculos dos Índices Finais (Alinhado com Etapa 3 e sua solicitação)
        ac = placeholders["ATIVO_CIRC_ATUAL"]
        pc = placeholders["PASS_CIRC_ATUAL"]
        est = placeholders.get("ESTOQUE_ATUAL", 0.0)
        disp = placeholders.get("DISPONIBILIDADES_ATUAL", 0.0)
        pl_atu = placeholders["PL_ATUAL"]
        
        # Dívida Total (Passivo Circ + Não Circ)
        divida_total = pc + placeholders["PASS_NAO_CIRC_ATUAL"]
        
        indices = {
            "liq_corrente": round(ac / pc, 2) if pc > 0 else 0.0, # Resulta 0.45 
            "liq_seca": round((ac - est) / pc, 2) if pc > 0 else 0.0,
            "liq_imediata": round(disp / pc, 2) if pc > 0 else 0.0, # Resulta 0.08
            "endiv_geral": round((divida_total / at_atu) * 100, 2) if at_atu > 0 else 0.0, # Resulta 183.68% 
            "margem_liquida": round((lucro_liq / receita_liq * 100), 2) if receita_liq > 0 else 0.0, # Resulta 4.96% 
            "roa": round((lucro_liq / at_atu * 100), 2) if at_atu > 0 else 0.0, # Resulta 16.16% 
            "roe": round((lucro_liq / pl_atu * 100), 2) if pl_atu > 0 else 0.0  # Resulta 19.31% 
        }

        # Sincronização de placeholders para o MetricsCalculator
        placeholders["RECEITA_LIQ_ATUAL"] = receita_liq
        placeholders["LUCRO_LIQ_ATUAL"] = lucro_liq

        return {
            "empresa": dados_por_ano[ano_atu]["balancete"]["metadata"].get("empresa", "EMPRESA NÃO IDENTIFICADA"),
            "tabela_patrimonial": tabela_patrimonial,
            "placeholders": placeholders,
            "indices": indices
        }