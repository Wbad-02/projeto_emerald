from flask import Flask, render_template, request, jsonify
from core.services.financial_service import FinancialService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/processar', methods=['POST'])
def processar():
    if 'pdf-input' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
    files = request.files.getlist('pdf-input')
    
    # O Service resolve toda a complexidade e retorna o dicionário pronto
    resultado_final = FinancialService.processar_arquivos(files)

    return jsonify(resultado_final)

if __name__ == '__main__':
    app.run(debug=True, port=5000)