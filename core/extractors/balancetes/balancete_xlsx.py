from core.extractors.balancetes._parser import _BalanceteParser


class BalanceteXlsxExtractor(_BalanceteParser):
    def execute(self):
        rows = self.read_excel_rows(engine="openpyxl")
        return self._extract_from_rows(rows)
