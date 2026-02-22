from core.extractors.dre import DreTxtExtractor
from core.extractors.balancete import BalanceteTxtExtractor
from core.utils.calculator_balancete import FinancialCalculator
from core.utils.calculator_dre import DreCalculator
from core.utils.converter import FileConverter

class FinancialService:
    @staticmethod
    def processar_arquivos(files):
        dados_por_ano = {}

        for file in files:
            filename_limpo = file.filename.upper().replace(".", "").replace("-", "")
            texto_limpo = FileConverter.to_text_stream(file)
            if not texto_limpo: continue

            if 'DRE' in filename_limpo or 'DEMONSTRACAO' in filename_limpo:
                extrator = DreTxtExtractor(texto_limpo)
                tipo = "dre"
            else:
                extrator = BalanceteTxtExtractor(texto_limpo)
                tipo = "balancete"

            resultado = extrator.execute()
            ano = str(resultado['metadata'].get('ano') or 'Desconhecido')
            if ano not in dados_por_ano:
                dados_por_ano[ano] = {"dre": None, "balancete": None}
            dados_por_ano[ano][tipo] = resultado

        dados_validos = {ano: d for ano, d in dados_por_ano.items() 
                        if ano != 'Desconhecido' and d["dre"] and d["balancete"]}
        
        if len(dados_validos) < 2:
            return {"error": "Dados insuficientes. Envie DRE e Balancete de pelo menos 2 anos."}

        rel_patrimonial = FinancialCalculator.processar_dashboard(dados_validos)
        rel_dre = DreCalculator.processar_dre(dados_validos)

        # Captura de dados para o Intelligence Insight
        rl_atual = rel_dre["placeholders"].get("RECEITA_LIQ_ATUAL", 0)
        ll_atual = rel_dre["placeholders"].get("LUCRO_LIQ_ATUAL", 0)

        # EXUCAÇÃO DO CÁLCULO TRIBUTÁRIO DETALHADO (Regras 2026)
        comparativo = FinancialService.calcular_tributacao_detalhada(rl_atual, ll_atual)

        return {
            "empresa": rel_patrimonial.get("empresa", "Empresa não Identificada"),
            "indices": rel_patrimonial.get("indices", {}),
            "tabela_patrimonial": rel_patrimonial.get("tabela_patrimonial", []),
            "tabela_dre": rel_dre.get("tabela", []),
            "comparativo_tributario": comparativo,
            "anos": dados_validos
        }

    @staticmethod
    def calcular_tributacao_detalhada(receita_anual, lucro_anual):
        # 1. SIMPLES NACIONAL (Anexo III - Serviços/Transporte) [cite: 61]
        if receita_anual <= 180000:
            simples = receita_anual * 0.06 [cite: 61]
        elif receita_anual <= 3600000:
            simples = (receita_anual * 0.21) - 125640  # Faixa 5 [cite: 64]
        else:
            simples = (receita_anual * 0.33) - 648000  # Faixa 6 [cite: 64]

        # 2. LUCRO PRESUMIDO (Específico para Transporte de Cargas) [cite: 67]
        base_irpj = receita_anual * 0.08  # 8% presunção para cargas [cite: 67]
        base_csll = receita_anual * 0.12  # 12% presunção para cargas [cite: 67]
        
        # IRPJ: 15% + 10% Adicional sobre o que exceder R$ 240k/ano 
        imposto_irpj = base_irpj * 0.15 + (max(0, base_irpj - 240000) * 0.10)
        imposto_csll = base_csll * 0.09   # 9% CSLL 
        pis_cofins = receita_anual * (0.0065 + 0.03) # PIS 0.65% + COFINS 3% 
        
        total_presumido = imposto_irpj + imposto_csll + pis_cofins

        # 3. LUCRO REAL (Alíquota efetiva estimada de 34%) [cite: 46]
        valor_lucro_real = round(lucro_anual * 0.34, 2) if lucro_anual > 0 else 0

        regimes = [
            {"nome": "Simples Nacional", "valor": round(simples, 2)},
            {"nome": "Lucro Presumido", "valor": round(total_presumido, 2)},
            {"nome": "Lucro Real", "valor": valor_lucro_real}
        ]
        
        # Lógica de destaque para o Front-end
        menor = min(r["valor"] for r in regimes)
        for r in regimes: 
            r["economica"] = (r["valor"] == menor)
            
        return regimes