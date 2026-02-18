class FinancialCalculator:
    @staticmethod
    def processar_dashboard(dados_por_ano):
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: return None

        ano_ant, ano_atu = anos[0], anos[1]
        p_ant = dados_por_ano[ano_ant]["balancete"]["resumo_grau_1"]
        p_atu = dados_por_ano[ano_atu]["balancete"]["resumo_grau_1"]

        # 1. Mapeamento das Chaves Base
        mapeamento = {
            "ATIVO_CIRCULANTE": "Ativo Circulante",
            "ATIVO_NAO_CIRCULANTE": "Ativo Não Circulante",
            "PASSIVO_CIRCULANTE": "Passivo Circulante",
            "PASSIVO_NAO_CIRCULANTE": "Passivo Não Circulante",
            "PATRIMONIO_LIQUIDO": "Patrimônio Líquido"
        }

        placeholders = {}
        tabela_patrimonial = []

        # 2. Processamento das contas individuais
        for js_key, bal_key in mapeamento.items():
            v_ant = abs(p_ant.get(bal_key, 0.0))
            v_atu = abs(p_atu.get(bal_key, 0.0))
            
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

        # --- 3. CÁLCULO DOS TOTAIS (Para o Gráfico de Evolução) ---
        # ATIVO TOTAL = Circulante + Não Circulante
        at_ant = placeholders["ATIVO_CIRCULANTE_ANT"] + placeholders["ATIVO_NAO_CIRCULANTE_ANT"]
        at_atu = placeholders["ATIVO_CIRCULANTE_ATUAL"] + placeholders["ATIVO_NAO_CIRCULANTE_ATUAL"]
        
        # PASSIVO TOTAL = Circulante + Não Circulante + PL
        pt_ant = placeholders["PASSIVO_CIRCULANTE_ANT"] + placeholders["PASSIVO_NAO_CIRCULANTE_ANT"] + placeholders["PATRIMONIO_LIQUIDO_ANT"]
        pt_atu = placeholders["PASSIVO_CIRCULANTE_ATUAL"] + placeholders["PASSIVO_NAO_CIRCULANTE_ATUAL"] + placeholders["PATRIMONIO_LIQUIDO_ATUAL"]

        # Salva nos placeholders com a nomenclatura que o JS espera (Gráfico 4)
        placeholders.update({
            "ATIVO_TOTAL_ANT": at_ant,
            "ATIVO_TOTAL_ATUAL": at_atu,
            "PASSIVO_TOTAL_ANT": pt_ant,
            "PASSIVO_TOTAL_ATUAL": pt_atu
        })

        # 4. Cálculos de Índices
        ac = placeholders["ATIVO_CIRCULANTE_ATUAL"]
        pc = abs(placeholders["PASSIVO_CIRCULANTE_ATUAL"])
        pc = pc if pc > 0 else 1.0 # Evita divisão por zero
        
        indices = {
            "liq_corrente": round(ac / pc, 2),
            "endiv_geral": round((pt_atu - placeholders["PATRIMONIO_LIQUIDO_ATUAL"]) / at_atu * 100, 2) if at_atu > 0 else 0
        }

        return {
            "empresa": dados_por_ano[ano_atu]["balancete"]["metadata"].get("empresa"),
            "tabela_patrimonial": tabela_patrimonial,
            "placeholders": placeholders,
            "indices": indices
        }