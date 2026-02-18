import re
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
            filename_original = file.filename.upper()
            
            # Converte para texto e limpa aspas e sujeiras de encoding
            texto_limpo = FileConverter.to_text_stream(file)
            if not texto_limpo: continue

            # --- IDENTIFICAÇÃO ROBUSTA ---
            nome_limpo = re.sub(r'[^A-Z]', '', filename_original)
            padrões_dre = ['DRE', 'DEMONSTRACAORESULTADO', 'RESULTADOEXERCICIO']
            
            if any(k in nome_limpo for k in padrões_dre) or 'D.R.E' in filename_original:
                extrator = DreTxtExtractor(texto_limpo)
                tipo = "dre"
            else:
                extrator = BalanceteTxtExtractor(texto_limpo)
                tipo = "balancete"

            resultado = extrator.execute()
            
            # Sanitização do Ano
            raw_ano = resultado.get('metadata', {}).get('ano')
            ano = str(raw_ano).strip() if raw_ano else 'Desconhecido'

            if ano not in dados_por_ano:
                dados_por_ano[ano] = {"dre": None, "balancete": None}
            
            dados_por_ano[ano][tipo] = resultado

        # Filtro de Integridade: Garante pares de documentos por ano
        dados_validos = {
            ano: dados for ano, dados in dados_por_ano.items() 
            if ano != 'Desconhecido' and dados["dre"] is not None and dados["balancete"] is not None
        }
        
        if not dados_validos:
            return {"error": "Não foi possível encontrar pares de DRE e Balancete para o mesmo ano."}

        # Processamento dos Relatórios (Calculadoras especializadas)
        rel_balancete = FinancialCalculator.processar_dashboard(dados_validos)
        rel_dre = DreCalculator.processar_dre(dados_validos)
        
        # --- CONSOLIDAÇÃO DE DADOS PARA O FRONT-END ---
        # Criamos um dicionário mestre de índices que contém todos os placeholders
        # Isso resolve o problema de valores zerados no JavaScript
        indices_consolidados = {}
        indices_consolidados.update(rel_balancete.get("indices", {}))
        indices_consolidados.update(rel_balancete.get("placeholders", {}))
        indices_consolidados.update(rel_dre.get("placeholders", {}))
        
        return {
            "empresa": rel_balancete.get("empresa", "Empresa não Identificada"),
            "anos": sorted(list(dados_validos.keys())),
            
            # Fonte unificada para cards e tabelas
            "indices": indices_consolidados,
            
            # Tabelas preparadas para renderização direta
            "tabela_patrimonial": rel_balancete.get("tabela_patrimonial", []),
            "tabela_dre": rel_dre.get("tabela", []), 
            
            # Mantemos as referências originais para compatibilidade
            "balancete": rel_balancete, 
            "dre": rel_dre,
        }