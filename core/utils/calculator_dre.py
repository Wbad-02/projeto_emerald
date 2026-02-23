class DreCalculator:
    @staticmethod
    def processar_dre(dados_por_ano):
        # 1. Ordenação e Validação de Períodos
        anos = sorted(dados_por_ano.keys())
        if len(anos) < 2: 
            return None

        ano_ant, ano_atu = anos[0], anos[1]
        
        def extrair_metricas(dados_dre):
            if not dados_dre or "indicadores_grau_1" not in dados_dre:
                return {k: 0.0 for k in ["RB", "RL", "LB", "DO", "RO", "LL", "EBITDA"]}

            ind = dados_dre["indicadores_grau_1"]
            contas = dados_dre.get("contas", [])
            
            # Mapeamento base
            rb = ind.get("RECEITA BRUTA", 0.0)
            rl = ind.get("RECEITA LIQUIDA", 0.0)
            lb = ind.get("LUCRO BRUTO", 0.0)
            do = ind.get("DESPESAS OPERACIONAIS", 0.0)
            
            # --- ADIÇÃO: CÁLCULO DO RESULTADO OPERACIONAL ---
            # Prioriza o valor extraído, senão calcula: Lucro Bruto - Despesas Operacionais
            ro = ind.get("RESULTADO OPERACIONAL", 0.0)
            if ro == 0:
                ro = lb - do  # Cálculo lógico se a linha estiver ausente ou zerada
            
            # Lógica para o Lucro Líquido (Final)
            ll = ind.get("LUCRO DO EXERCICIO", 0.0) or ind.get("PREJUIZO DO EXERCICIO", 0.0)
            if ll == 0:
                ll = ro # Fallback para o operacional se não houver a linha final

            # Cálculo do EBITDA: Resultado Operacional + Depreciação
            depreciacao = sum(
                abs(c.get('valor', 0.0)) 
                for c in contas 
                if any(termo in c.get('descricao', '').upper() for termo in ["DEPRECIACAO", "AMORTIZACAO"])
            )
            
            return {
                "RB": rb, 
                "RL": rl, 
                "LB": lb, 
                "DO": do, 
                "RO": ro, # <-- Novo campo
                "LL": ll,
                "EBITDA": ro + depreciacao # EBITDA usa RO como base, não LL
            }

        # 2. Extração das Métricas por Ano
        m_ant = extrair_metricas(dados_por_ano[ano_ant].get("dre"))
        m_atu = extrair_metricas(dados_por_ano[ano_atu].get("dre"))

        # --- ADIÇÃO: MAPEAMENTO PARA O DASHBOARD ---
        map_placeholders = {
            "RECEITA_BRUTA": "RB", 
            "RECEITA_LIQ": "RL", 
            "LUCRO_BRUTO": "LB", 
            "DESP_OP": "DO", 
            "RESULTADO_OPER": "RO", # <-- Adicionado para gerar os cards/tabela
            "EBITDA": "EBITDA", 
            "LUCRO_LIQ": "LL"
        }

        placeholders = {}
        tabela = []

        for p_key, m_key in map_placeholders.items():
            v_ant = m_ant[m_key]
            v_atu = m_atu[m_key]
            
            # 3. CÁLCULO DE VARIAÇÃO
            variacao = v_atu - v_ant
            percentual = (variacao / abs(v_ant) * 100) if v_ant != 0 else 0.0
            
            if percentual > 0.5: status = "▲ Crescimento"
            elif percentual < -0.5: status = "▼ Queda"
            else: status = "● Estável"

            placeholders.update({
                f"{p_key}_ANT": v_ant, 
                f"{p_key}_ATUAL": v_atu,
                f"{p_key}_VAR": variacao, 
                f"{p_key}_PERC": round(percentual, 2),
                f"{p_key}_STATUS": status
            })

            tabela.append({
                "conta": p_key.replace('_', ' ').title(),
                "anterior": v_ant, 
                "atual": v_atu,
                "perc": round(percentual, 2), 
                "status": status
            })

        return {"placeholders": placeholders, "tabela": tabela}