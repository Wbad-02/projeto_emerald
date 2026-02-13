class FinancialCalculator:
    @staticmethod
    def gerar_tabela_comparativa(dados_por_ano):
        # Ordenamos os anos para garantir que o menor seja o "Anterior"
        anos_ordenados = sorted(dados_por_ano.keys())
        
        if len(anos_ordenados) < 2:
            return [] # Necessário ao menos dois anos para comparar

        ano_ant = anos_ordenados[0]
        ano_atu = anos_ordenados[1]

        # Mapeamento: (Chave de busca, Nome de exibição na tabela, Origem)
        contas_para_comparar = [
            ("1.1", "Ativo Circulante", "balancete"),
            ("1.2", "Ativo Não Circulante", "balancete"),
            ("1", "Ativo Total", "balancete"),
            ("2.1", "Passivo Circulante", "balancete"),
            ("2.3", "Patrimônio Líquido", "balancete"),
            ("RECEITA BRUTA", "Receita Bruta", "dre"),
            ("RECEITA LIQUIDA", "Receita Líquida", "dre"),
            ("LUCRO BRUTO", "Lucro Bruto", "dre"),
            ("LUCRO LIQUIDO", "Lucro Líquido", "dre")
        ]

        comparativo = []

        for chave, nome, origem in contas_para_comparar:
            v_ant = FinancialCalculator._buscar_valor(dados_por_ano[ano_ant], chave, origem)
            v_atu = FinancialCalculator._buscar_valor(dados_por_ano[ano_atu], chave, origem)
            
            variacao = v_atu - v_ant
            # Evita divisão por zero se o ano anterior estiver zerado
            percentual = (variacao / abs(v_ant) * 100) if v_ant != 0 else 0

            comparativo.append({
                "conta": nome,
                "anterior": v_ant,
                "atual": v_atu,
                "variacao": variacao,
                "status_percentual": round(percentual, 2)
            })

        return comparativo

    @staticmethod
    def _buscar_valor(pacote_ano, chave, origem):
        """Busca o valor no sub-bloco correto (balancete ou dre)"""
        if not pacote_ano or not pacote_ano.get(origem):
            return 0.0
        
        dados = pacote_ano[origem]
        if origem == "balancete":
            # Busca no resumo_grau_1 (ex: '1', '1.1')
            return dados.get("resumo_grau_1", {}).get(chave, {}).get("valor", 0.0)
        else:
            # Busca nos indicadores_grau_1 (ex: 'RECEITA BRUTA')
            return dados.get("indicadores_grau_1", {}).get(chave, 0.0)