from flask import Flask, render_template, request, jsonify
from core.services.financial_service import FinancialService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/processar', methods=['POST'])
def processar():
    # Deve bater com o nome usado no formData.append()
    arquivos = request.files.getlist('files') 
    if not arquivos:
        return jsonify({"error": "Nenhum arquivo recebido"}), 400
    
    resultado = FinancialService.processar_arquivos(arquivos)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, port=5000)