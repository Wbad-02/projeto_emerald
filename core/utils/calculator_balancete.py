class FinancialCalculator:
    @staticmethod
    def processar_dashboard(dados_por_ano):
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: return None

        ano_ant, ano_atu = anos[0], anos[1]
        
        # Acesso aos dados brutos extraídos
        b_ant = dados_por_ano[ano_ant]["balancete"]["resumo_grau_1"]
        b_atu = dados_por_ano[ano_atu]["balancete"]["resumo_grau_1"]
        
        # NOVO: Acesso aos dados da DRE para cálculo de rentabilidade
        d_atu = dados_por_ano[ano_atu]["dre"]["indicadores_grau_1"]

        # 1. Mapeamento das Chaves Patrimoniais
        mapeamento = {
            "ATIVO_CIRCULANTE": "Ativo Circulante",
            "ATIVO_NAO_CIRCULANTE": "Ativo Não Circulante",
            "PASSIVO_CIRCULANTE": "Passivo Circulante",
            "PASSIVO_NAO_CIRCULANTE": "Passivo Não Circulante",
            "PATRIMONIO_LIQUIDO": "Patrimônio Líquido"
        }

        placeholders = {}
        tabela_patrimonial = []

        # 2. Processamento das variações patrimoniais
        for js_key, bal_key in mapeamento.items():
            v_ant = abs(b_ant.get(bal_key, 0.0))
            v_atu = abs(b_atu.get(bal_key, 0.0))
            
            var = v_atu - v_ant
            perc = (var / v_ant * 100) if v_ant != 0 else 0.0
            status_str = "▲ Crescimento" if perc > 0.5 else "▼ Queda" if perc < -0.5 else "● Estável"

            placeholders.update({
                f"{js_key}_ANT": v_ant,
                f"{js_key}_ATUAL": v_atu,
                f"{js_key}_PERC": round(perc, 2),
                f"{js_key}_STATUS": status_str
            })

            tabela_patrimonial.append({
                "conta": bal_key,
                "anterior": v_ant,
                "atual": v_atu,
                "perc": round(perc, 2),
                "status": status_str
            })

        # 3. Totais para Gráficos e Índices
        at_atu = placeholders["ATIVO_CIRCULANTE_ATUAL"] + placeholders["ATIVO_NAO_CIRCULANTE_ATUAL"]
        pt_atu = (placeholders["PASSIVO_CIRCULANTE_ATUAL"] + 
                  placeholders["PASSIVO_NAO_CIRCULANTE_ATUAL"] + 
                  placeholders["PATRIMONIO_LIQUIDO_ATUAL"])

        # 4. Extração de valores para Rentabilidade (Margem e ROA)
        # Tenta capturar o Lucro do Exercício, senão usa o Operacional como fallback
        lucro_liq = d_atu.get("LUCRO DO EXERCICIO", 0.0) or d_atu.get("RESULTADO OPERACIONAL", 0.0)
        receita_liq = d_atu.get("RECEITA LIQUIDA", 0.0)

        # 5. Cálculos dos Índices Finais
        ac = placeholders["ATIVO_CIRCULANTE_ATUAL"]
        pc = abs(placeholders["PASSIVO_CIRCULANTE_ATUAL"]) or 1.0 # Evita divisão por zero
        
        indices = {
            "liq_corrente": round(ac / pc, 2),
            "endiv_geral": round((pt_atu - placeholders["PATRIMONIO_LIQUIDO_ATUAL"]) / at_atu * 100, 2) if at_atu > 0 else 0,
            # NOVO: Margem Líquida (Eficiência sobre Vendas)
            "margem_liquida": round((lucro_liq / receita_liq * 100), 2) if receita_liq > 0 else 0,
            # NOVO: ROA (Eficiência sobre Ativos/Estrutura)
            "roa": round((lucro_liq / at_atu * 100), 2) if at_atu > 0 else 0
        }

        return {
            "empresa": dados_por_ano[ano_atu]["balancete"]["metadata"].get("empresa"),
            "tabela_patrimonial": tabela_patrimonial,
            "placeholders": placeholders,
            "indices": indices
        }