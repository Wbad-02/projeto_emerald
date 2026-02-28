from core.extractors.dre._parser import _DreParser


class DreXlsExtractor(_DreParser):
    def execute(self):
        rows = self.read_excel_rows(engine="xlrd")
        return self._extract_from_rows(rows)
