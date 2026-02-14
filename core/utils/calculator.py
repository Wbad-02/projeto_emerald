class FinancialCalculator:
    @staticmethod
    def processar_dashboard(dados_por_ano):
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: return None

        ano_ant, ano_atu = anos[0], anos[1]
        p_ant = dados_por_ano[ano_ant]["balancete"].get("resumo_grau_1", {})
        p_atu = dados_por_ano[ano_atu]["balancete"].get("resumo_grau_1", {})
        
        empresa = dados_por_ano[ano_atu]["balancete"]["metadata"].get("empresa", "Empresa Desconhecida")

        mapeamento = [("1", "Ativo Total"), ("1.1", "Ativo Circulante"), 
                      ("2.1", "Passivo Circulante"), ("2.3", "Patrimônio Líquido")]

        comparativo = []
        for cod, label in mapeamento:
            v_ant = p_ant.get(cod, {}).get("valor", 0.0)
            v_atu = p_atu.get(cod, {}).get("valor", 0.0)
            
            variacao = v_atu - v_ant
            percentual = (variacao / abs(v_ant) * 100) if v_ant != 0 else 0
            
            comparativo.append({
                "conta": label, "anterior": v_ant, "atual": v_atu,
                "perc": round(percentual, 2),
                "status": "▲ Crescimento" if percentual > 0.5 else ("▼ Queda" if percentual < -0.5 else "● Estável")
            })

        # Cálculo de Liquidez
        ac = p_atu.get("1.1", {}).get("valor", 0.0)
        pc = p_atu.get("2.1", {}).get("valor", 0.0)
        liq = round(ac / pc, 2) if pc != 0 else 0

        return {"empresa": empresa, "tabela": comparativo, "liquidez": liq}