from core.extractors.dre._parser import _DreParser


class DreXlsxExtractor(_DreParser):
    def execute(self):
        rows = self.read_excel_rows(engine="openpyxl")
        return self._extract_from_rows(rows)
