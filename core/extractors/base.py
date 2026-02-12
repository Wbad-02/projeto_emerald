import pandas as pd
import io


class BaseExcelExtractor:

    def __init__(self, uploaded_file):
        self.file = uploaded_file

    def read_excel(self):
        content = self.file.read()
        self.file.seek(0)

        try:
            return pd.read_excel(io.BytesIO(content), header=None)
        except Exception as e:
            print("Erro ao ler arquivo:", e)
            return None
