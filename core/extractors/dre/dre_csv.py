from core.extractors.dre._parser import _DreParser


class DreCsvExtractor(_DreParser):
    def execute(self):
        rows = self.read_csv_rows()
        return self._extract_from_rows(rows)
