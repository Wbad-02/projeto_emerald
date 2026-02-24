class FinancialMetricsCalculator:
    @staticmethod
    def calcular_indices(p_bal, p_dre):
        """
        Calcula os índices que estavam zerados no dashboard.
        Usa as chaves confirmadas pelo log de debug (PASS_CIRC_ATUAL, etc).
        """
        # --- 1. CAPTURA DE VARIÁVEIS (Nomes sincronizados com o Debug) ---
        ac = p_bal.get('ATIVO_CIRC_ATUAL', 0)
        anc = p_bal.get('ATIVO_NAO_CIRC_ATUAL', 0)
        
        # O debug confirmou que a chave é 'PASS_CIRC_ATUAL'
        pc = abs(p_bal.get('PASS_CIRC_ATUAL', 0)) 
        pnc = abs(p_bal.get('PASS_NAO_CIRC_ATUAL', 0))
        pl = abs(p_bal.get('PL_ATUAL', 1)) 
        
        # --- 2. VARIÁVEIS DE PERFORMANCE (DRE) ---
        rl = p_dre.get('RECEITA_LIQ_ATUAL', 0)
        ll = p_dre.get('LUCRO_LIQ_ATUAL', 0)

        # --- 3. CÁLCULOS TÉCNICOS ---
        ativo_total = ac + anc
        passivo_exigivel = pc + pnc

        return {
            # Liquidez Corrente (Resultado esperado: 0.45)
            "liq_corrente": round(ac / pc, 2) if pc > 0 else 0,
            
            # Endividamento Geral (Passivo / Ativo | Resultado esperado: 183.68%)
            "endiv_geral": round((passivo_exigivel / ativo_total) * 100, 2) if ativo_total > 0 else 0,
            
            # Rentabilidades (Já estavam funcionando no debug)
            "margem_liquida": round((ll / rl) * 100, 2) if rl > 0 else 0,
            "roa": round((ll / ativo_total) * 100, 2) if ativo_total > 0 else 0,
            "roe": round((ll / pl) * 100, 2) if pl > 0 else 0
        }