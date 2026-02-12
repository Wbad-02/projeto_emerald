from flask import Flask, render_template, request, jsonify
from core.extractors.balancete import BalanceteCsvExtractor
from core.extractors.dre import DreCsvExtractor

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/processar', methods=['POST'])
def processar():
    if 'pdf-input' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
    files = request.files.getlist('pdf-input')
    consolidado = {}

    for file in files:
        name = file.filename.lower()
        # Decisão baseada no nome do arquivo
        if 'balancete' in name:
            extractor = BalanceteCsvExtractor(file)
        elif 'dre' in name:
            extractor = DreCsvExtractor(file)
        else: continue
            
        consolidado[file.filename] = extractor.execute()

    return jsonify(consolidado)

if __name__ == '__main__':
    app.run(debug=True)