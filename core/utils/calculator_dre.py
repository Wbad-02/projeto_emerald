class DreCalculator:
    @staticmethod
    def processar_dre(dados_por_ano):
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: return None

        ano_ant, ano_atu = anos[0], anos[1]
        
        def extrair_metricas(dados_dre):
            # Validação Defensiva
            if not dados_dre or "indicadores_grau_1" not in dados_dre:
                return {k: 0.0 for k in ["RB", "RL", "LB", "DO", "LL", "EBITDA"]}

            ind = dados_dre["indicadores_grau_1"]
            contas = dados_dre.get("contas", [])
            
            # Soma depreciações para o EBITDA (Busca em subcontas)
            depreciacao = sum(abs(c['valor']) for c in contas if "DEPRECIACAO" in c.get('descricao', '').upper())
            
            rb = ind.get("RECEITA BRUTA", 0.0)
            rl = ind.get("RECEITA LIQUIDA", 0.0)
            lb = ind.get("LUCRO BRUTO", 0.0)
            do = ind.get("DESPESAS OPERACIONAIS", 0.0)
            
            # Lógica de captura de Lucro/Prejuízo
            ll = ind.get("RESULTADO OPERACIONAL", 0.0)
            if ll == 0:
                ll = ind.get("PREJUIZO DO EXERCICIO", 0.0) or ind.get("LUCRO DO EXERCICIO", 0.0)
            
            return {
                "RB": rb, "RL": rl, "LB": lb, "DO": do, "LL": ll,
                "EBITDA": ll + depreciacao
            }

        # Extração Segura
        m_ant = extrair_metricas(dados_por_ano[ano_ant].get("dre"))
        m_atu = extrair_metricas(dados_por_ano[ano_atu].get("dre"))

        map_placeholders = {
            "RECEITA_BRUTA": "RB", "RECEITA_LIQ": "RL", 
            "LUCRO_BRUTO": "LB", "DESP_OP": "DO", 
            "EBITDA": "EBITDA", "LUCRO_LIQ": "LL"
        }

        placeholders = {}
        tabela = []

        for p_key, m_key in map_placeholders.items():
            v_ant = m_ant[m_key]
            v_atu = m_atu[m_key]
            
            variacao = v_atu - v_ant
            perc = (variacao / abs(v_ant) * 100) if v_ant != 0 else 0
            
            if perc > 0.5: status = "▲ Crescimento"
            elif perc < -0.5: status = "▼ Queda"
            else: status = "● Estável"

            placeholders.update({
                f"{p_key}_ANT": v_ant, 
                f"{p_key}_ATUAL": v_atu,
                f"{p_key}_VAR": variacao, 
                f"{p_key}_PERC": round(perc, 2),
                f"{p_key}_STATUS": status
            })

            tabela.append({
                "conta": p_key.replace('_', ' ').title(),
                "anterior": v_ant, 
                "atual": v_atu,
                "perc": round(perc, 2), 
                "status": status
            })

        return {"placeholders": placeholders, "tabela": tabela}