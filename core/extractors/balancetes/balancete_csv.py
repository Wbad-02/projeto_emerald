from core.extractors.balancetes._parser import _BalanceteParser


class BalanceteCsvExtractor(_BalanceteParser):
    def execute(self):
        rows = self.read_csv_rows()
        return self._extract_from_rows(rows)
