import json

from flask import Flask, jsonify, request
from flask_cors import CORS

from core.services.dashboard_service import DashboardService, DashboardServiceError
from core.services.financial_service import FinancialService

app = Flask(__name__)
CORS(app)


@app.route('/processar', methods=['POST'])
def processar():
    if 'files' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado para análise."}), 400

    files = request.files.getlist('files')

    try:
        resultado = FinancialService.processar_arquivos(files)
        if "error" in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado)
    except Exception as e:
        print(f"Erro interno: {e}")
        return jsonify({"error": "Falha no processamento interno dos documentos."}), 500


@app.route('/api/dashboard/generate', methods=['POST'])
def generate_dashboard():
    if 'files' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado para análise."}), 400

    files = request.files.getlist('files')
    raw_year_map = request.form.get('file_years', '{}')

    try:
        year_map = json.loads(raw_year_map) if raw_year_map else {}
    except json.JSONDecodeError:
        return jsonify({"error": "Mapeamento de anos inválido."}), 400

    if not isinstance(year_map, dict):
        return jsonify({"error": "Mapeamento de anos inválido."}), 400

    normalized_year_map = {}
    for file_name, year in year_map.items():
        try:
            year_value = int(year)
        except (TypeError, ValueError):
            return jsonify({"error": f"Ano inválido para arquivo '{file_name}'."}), 400

        if year_value < 1900 or year_value > 2100:
            return jsonify({"error": f"Ano inválido para arquivo '{file_name}'."}), 400

        normalized_year_map[str(file_name)] = year_value

    try:
        payload = DashboardService.generate_dashboard(files, normalized_year_map)
        return jsonify(payload)
    except DashboardServiceError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        print(f"Erro interno: {exc}")
        return jsonify({"error": "Falha no processamento interno dos documentos."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
