import csv

from core.extractors.balancetes._parser import _BalanceteParser


class BalancetePdfExtractor(_BalanceteParser):
    def execute(self):
        lines = self.read_pdf_lines()
        rows = [next(csv.reader([line])) for line in lines if line.strip()]
        return self._extract_from_rows(rows)
