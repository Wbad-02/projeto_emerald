from core.extractors.dre import DreTxtExtractor
from core.extractors.balancete import BalanceteTxtExtractor

from core.utils.calculator import FinancialCalculator
from core.utils.calculator_dre import DreCalculator
from core.utils.converter import FileConverter

class FinancialService:
    @staticmethod
    def processar_arquivos(files):
        dados_por_ano = {}

        for file in files:
            # 1. Normalização do nome para busca
            filename_original = file.filename.upper()
            filename_limpo = filename_original.replace(".", "").replace("-", "")
            
            texto_limpo = FileConverter.to_text_stream(file)
            if not texto_limpo: continue

            # 2. Identificação robusta do tipo
            # Agora aceita 'DRE', 'D.R.E.', 'D-R-E' etc.
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
            
            # 3. Armazenamento (O erro anterior sobrescrevia o balancete aqui)
            dados_por_ano[ano][tipo] = resultado

        # 4. Filtro de Integridade
        dados_validos = {
            ano: dados for ano, dados in dados_por_ano.items() 
            if ano != 'Desconhecido' and dados["dre"] is not None and dados["balancete"] is not None
        }
        
        if len(dados_validos) < 2:
            return {"error": "Dados insuficientes. Certifique-se de que os arquivos de DRE contenham 'DRE' no nome."}

        # Prossegue para os cálculos...
        relatorio_patrimonial = FinancialCalculator.processar_dashboard(dados_validos)
        relatorio_dre = DreCalculator.processar_dre(dados_validos)
        
        return {
            "empresa": relatorio_patrimonial.get("empresa", "Empresa não Identificada"),
            "indices": relatorio_patrimonial.get("indices", {}),
            "tabela_patrimonial": relatorio_patrimonial.get("tabela", []),
            "tabela_dre": relatorio_dre.get("tabela", []),
            "balancete": relatorio_patrimonial.get("placeholders", {}), # Adicionado
            "dre": relatorio_dre.get("placeholders", {}),               # Adicionado
            "anos": dados_por_ano 
}