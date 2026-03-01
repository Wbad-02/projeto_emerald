import io

from core.services.dashboard_service import DashboardService


class MockUpload:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.stream = io.BytesIO(content)


def test_normalize_number_ptbr():
    assert DashboardService.normalize_number('1.234,56') == 1234.56
    assert DashboardService.normalize_number('R$ 2.000,00') == 2000.0


def test_parse_balancete_and_indices_div_zero():
    csv = (
        'codigo;descricao;saldo\n'
        '1.1.01;Ativo Circulante;1000,00\n'
        '1.2.00;Ativo Não Circulante;500,00\n'
        '2.1.00;Passivo Circulante;0,00\n'
        '2.2.00;Passivo Não Circulante;100,00\n'
        '2.3.00;Patrimônio Líquido;1400,00\n'
    ).encode()
    dre = (
        'descricao;valor\n'
        'Receita Bruta;2000,00\n'
        'Receita Líquida;1800,00\n'
        'Lucro Líquido;200,00\n'
    ).encode()

    bal_file = MockUpload('balancete-2024.csv', csv)
    dre_file = MockUpload('dre-2024.csv', dre)

    dados = {
        2024: {
            'balancete': DashboardService.parse_balancete(bal_file, 2024),
            'dre': DashboardService.parse_dre(dre_file, 2024),
        }
    }

    placeholders = DashboardService.compute_metrics(dados)
    assert placeholders['ATIVO_TOTAL_2024'] == 1500.0
    assert placeholders['PASSIVO_TOTAL_2024'] == 1500.0
    assert 'Estoques não localizados; usado valor 0.' in placeholders['warnings']


def test_variation_between_years():
    dados = {
        2023: {'balancete': {'ATIVO_CIRC': 100, 'ATIVO_NAO_CIRC': 100, 'PASS_CIRC': 100, 'PASS_NAO_CIRC': 0, 'PL': 100, 'ATIVO_TOTAL_2023': 200, 'PASSIVO_TOTAL_2023': 200}, 'dre': {'RECEITA_LIQ': 100, 'LUCRO_LIQ': 10}},
        2024: {'balancete': {'ATIVO_CIRC': 100, 'ATIVO_NAO_CIRC': 150, 'PASS_CIRC': 100, 'PASS_NAO_CIRC': 50, 'PL': 100, 'ATIVO_TOTAL_2024': 250, 'PASSIVO_TOTAL_2024': 250}, 'dre': {'RECEITA_LIQ': 120, 'LUCRO_LIQ': 12, 'RECEITA_BRUTA': 130}},
    }
    placeholders = DashboardService.compute_metrics(dados)
    comp = placeholders['COMPARACOES']['RECEITA_LIQ']
    assert comp['var'] == 20
    assert round(comp['perc'], 2) == 20.0
    assert comp['status'].startswith('▲')


def test_detect_statement_type_by_content():
    dre_csv = (
        'descricao;valor\n'
        'Receita Líquida;1800,00\n'
        'Lucro Líquido;200,00\n'
    ).encode()

    upload = MockUpload('relatorio.csv', dre_csv)
    assert DashboardService.detect_statement_type(upload) == 'dre'


def test_generate_dashboard_with_unknown_filename_uses_content_detection():
    bal_csv = (
        'codigo;descricao;saldo\n'
        '1.1.01;Ativo Circulante;1000,00\n'
        '2.1.00;Passivo Circulante;500,00\n'
        '2.3.00;Patrimônio Líquido;500,00\n'
    ).encode()
    dre_csv = (
        'descricao;valor\n'
        'Receita Bruta;2000,00\n'
        'Receita Líquida;1800,00\n'
        'Lucro Líquido;200,00\n'
    ).encode()

    files = [
        MockUpload('arquivo_a_2024.csv', bal_csv),
        MockUpload('arquivo_b_2024.csv', dre_csv),
    ]

    payload = DashboardService.generate_dashboard(files, {})
    assert payload['anos_detectados'] == [2024]
    assert payload['placeholders']['RECEITA_LIQ_2024'] == 1800.0
