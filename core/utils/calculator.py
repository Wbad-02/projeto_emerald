class FinancialCalculator:
    @staticmethod
    def processar_dashboard(dados_por_ano):
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: return None

        ano_ant, ano_atu = anos[0], anos[1]
        p_ant = dados_por_ano[ano_ant]["balancete"]["resumo_grau_1"]
        p_atu = dados_por_ano[ano_atu]["balancete"]["resumo_grau_1"]

        def calcular_variacao(atual, anterior):
            """Lógica de status unificada para Balancete e DRE"""
            variacao = atual - anterior
            percentual = (variacao / abs(anterior) * 100) if anterior != 0 else 0
            
            if percentual > 0.5: status = "▲ Crescimento"
            elif percentual < -0.5: status = "▼ Queda"
            else: status = "● Estável"
            
            return variacao, round(percentual, 2), status

        # Grupos para a Tabela Comparativa
        mapeamento = [
            ("1", "Ativo Total"), ("1.1", "Ativo Circulante"), 
            ("1.2", "Ativo Não Circulante"), ("2.1", "Passivo Circulante"), 
            ("2.2", "Passivo Não Circulante"), ("2.3", "Patrimônio Líquido")
        ]

        tabela_comparativa = []
        for cod, label in mapeamento:
            v_ant = p_ant.get(cod, {}).get("valor", 0.0)
            v_atu = p_atu.get(cod, {}).get("valor", 0.0)
            
            v_nom, v_perc, v_status = calcular_variacao(v_atu, v_ant)
            
            tabela_comparativa.append({
                "conta": label, "anterior": v_ant, "atual": v_atu,
                "variacao": v_nom, "perc": v_perc, "status": v_status
            })

        # Totais e Índices (Fórmulas mantidas do equilíbrio A = P + PL)
        res_atu = {k: p_atu.get(k, {}).get("valor", 0.0) for k in ["1.1", "1.2", "2.1", "2.2", "2.3", "1.1.01"]}
        at = res_atu["1.1"] + res_atu["1.2"]
        exigivel = res_atu["2.1"] + res_atu["2.2"]

        return {
            "empresa": dados_por_ano[ano_atu]["balancete"]["metadata"].get("empresa"),
            "tabela": tabela_comparativa,
            "placeholders": {
                "ATIVO_TOTAL_ATUAL": at,
                "PASSIVO_TOTAL_ATUAL": res_atu["2.1"] + res_atu["2.2"] + res_atu["2.3"]
            },
            "indices": {
                "liq_corrente": round(res_atu["1.1"] / res_atu["2.1"], 2) if res_atu["2.1"] != 0 else 0,
                "endiv_geral": round((exigivel / at * 100), 2) if at != 0 else 0
            }
        }