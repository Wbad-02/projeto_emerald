import pandas as pd
from pypdf import PdfReader
import io

class FileConverter:
    @staticmethod
    def to_text_stream(file_storage):
        """
        Converte o arquivo para fluxo de texto único.
        
        LÓGICA DE "RENOMEAR":
        Se o arquivo não for binário (Excel/PDF), nós ignoramos a extensão original (.csv, .ret, etc)
        e forçamos a leitura como TEXTO (.txt), limpando as aspas do sistema contábil.
        """
        filename = file_storage.filename.lower()
        content = ""
        
        # Garante leitura do início
        file_storage.seek(0)

        try:
            # GRUPO 1: Binários (Não podem ser lidos como texto direto)
            if filename.endswith(('.xls', '.xlsx')):
                try:
                    # Excel: transforma as células em texto visual
                    df = pd.read_excel(file_storage, header=None, dtype=str)
                    content = df.to_string(index=False, header=False, na_rep="")
                except: return ""

            elif filename.endswith('.pdf'):
                try:
                    reader = PdfReader(file_storage)
                    content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                except: return ""

            # GRUPO 2: TODO O RESTO (A Lógica de "Mudar para .txt")
            # Aqui caem: .csv, .txt, .dat, .ret
            # Nós ignoramos a extensão e lemos os bytes brutos como texto.
            else:
                raw_bytes = file_storage.read()
                
                # Tenta decodificar (Latin-1 é o padrão de sistemas contábeis BR antigos)
                try:
                    content = raw_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        content = raw_bytes.decode('latin-1')
                    except:
                        content = raw_bytes.decode('utf-8', errors='ignore')

        except Exception as e:
            print(f"Erro na conversão de {filename}: {e}")
            return ""

        # --- LIMPEZA DE "SUJEIRA" (Aspas do CSV Falso) ---
        # O arquivo da Itasul vem como: "RECEITA... 100,00"
        # Ao tratar como txt, precisamos remover essas aspas para o regex funcionar.
        
        lines_limpas = []
        for line in content.splitlines():
            # Remove aspas duplas, simples e espaços extras nas pontas
            # Transforma: "RECEITA BRUTA     100,00"
            # Em:          RECEITA BRUTA     100,00
            clean_line = line.replace('"', '').replace("'", "").strip()
            
            if clean_line:
                lines_limpas.append(clean_line)
        
        return "\n".join(lines_limpas)