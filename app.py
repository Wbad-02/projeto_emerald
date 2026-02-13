from flask import Flask, render_template, request, jsonify
from core.utils.converter import FileConverter
from core.extractors.dre import DreTxtExtractor
from core.extractors.balancete import BalanceteTxtExtractor
from core.utils.calculator import FinancialCalculator # Importação do motor de cálculo
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/processar', methods=['POST'])
def processar():
    if 'pdf-input' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
    files = request.files.getlist('pdf-input')
    
    # Estrutura: { "2023": {"dre": {...}, "balancete": {...}}, "2024": {...} }
    dados_por_ano = {}

    for file in files:
        filename = file.filename.lower()
        texto_limpo = FileConverter.to_text_stream(file)
        
        if not texto_limpo: continue

        # Processa e captura metadados (incluindo o Ano)
        if 'dre' in filename:
            extrator = DreTxtExtractor(texto_limpo)
            resultado = extrator.execute()
            tipo = "dre"
        else:
            extrator = BalanceteTxtExtractor(texto_limpo)
            resultado = extrator.execute()
            tipo = "balancete"

        # Pega o ano identificado no cabeçalho do arquivo
        ano = resultado['metadata'].get('ano', 'Desconhecido')
        
        if ano not in dados_por_ano:
            dados_por_ano[ano] = {"dre": None, "balancete": None}
            
        dados_por_ano[ano][tipo] = resultado

    # GERAR DADOS PARA A TABELA COMPARATIVA
    # O motor de cálculo cruza automaticamente os valores dos anos detetados
    tabela_analise = FinancialCalculator.gerar_tabela_comparativa(dados_por_ano)

    # Retorna o dicionário organizado por anos e o array comparativo
    return jsonify({
        "empresa": "ITASUL TRANSPORTE E LOGISTICA LTDA",
        "anos": dados_por_ano,
        "comparativo": tabela_analise # Dados prontos para a tabela com as 5 colunas
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)