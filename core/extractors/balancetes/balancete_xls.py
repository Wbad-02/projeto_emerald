from core.extractors.balancetes._parser import _BalanceteParser


class BalanceteXlsExtractor(_BalanceteParser):
    def execute(self):
        rows = self.read_excel_rows(engine="xlrd")
        return self._extract_from_rows(rows)
