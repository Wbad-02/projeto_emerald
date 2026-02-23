from flask import Flask, request, jsonify
from flask_cors import CORS
from core.services.financial_service import FinancialService

app = Flask(__name__)
# O CORS é vital: ele autoriza o seu index.html (da porta 5500) a falar com o Flask (porta 5000)
CORS(app)

@app.route('/processar', methods=['POST'])
def processar():
    # Verifica se os arquivos foram enviados no FormData
    if 'files' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado para análise."}), 400
    
    files = request.files.getlist('files')
    
    try:
        # O Maestro processa, calcula margens, ROA e organiza os anos
        resultado = FinancialService.processar_arquivos(files)
        
        if "error" in resultado:
            return jsonify(resultado), 400
            
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Erro interno: {e}")
        return jsonify({"error": "Falha no processamento interno dos documentos."}), 500

if __name__ == '__main__':
    # Roda na porta 5000 por padrão
    app.run(debug=True, port=5000)