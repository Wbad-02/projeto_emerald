import pandas as pd
from pypdf import PdfReader
import io

class FileConverter:
    @staticmethod
    def to_text_stream(file_storage):
        filename = file_storage.filename.lower()
        content = ""
        file_storage.seek(0)
        raw_bytes = file_storage.read()

        try:
            if filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(raw_bytes), header=None, dtype=str)
                content = df.to_string(index=False, header=False, na_rep="")
            elif filename.endswith('.pdf'):
                reader = PdfReader(io.BytesIO(raw_bytes))
                content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            else:
                # Tenta decodificações comuns em ordem de probabilidade
                for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-16']:
                    try:
                        content = raw_bytes.decode(enc)
                        break
                    except: continue
        except Exception as e:
            print(f"Erro na conversão: {e}")
            return ""

        return content.strip()