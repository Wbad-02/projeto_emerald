import csv

from core.extractors.dre._parser import _DreParser


class DrePdfExtractor(_DreParser):
    def execute(self):
        lines = self.read_pdf_lines()
        rows = [next(csv.reader([line])) for line in lines if line.strip()]
        return self._extract_from_rows(rows)
