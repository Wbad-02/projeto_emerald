import re

class BalanceteTxtExtractor:
    def __init__(self, text_content):
        self.content = text_content
        self.grupos_grau_1 = {} 
        self.metadata = {"empresa": "ITASUL TRANSPORTE E LOGISTICA LTDA", "cnpj": ""}

    def execute(self):
        lines = self.content.splitlines()
        contas = []

        # 1. Captura o Ano do Período
        for line in lines:
            if "Período:" in line:
                match_ano = re.search(r'(\d{4})', line)
                if match_ano: self.metadata["ano"] = match_ano.group(1)

        # 2. Processamento das Contas
        for line in lines:
            # Identifica linhas de conta (começam com Código e Classificação)
            if not re.match(r'^\d', line): continue
            
            # --- LÓGICA DE EXTRAÇÃO POR BLOCOS ---
            
            # BLOCO A: Descrição (está antes das 4 vírgulas)
            # Ex: 010000,1,,ATIVO,,,,1,393...
            partes_principais = line.split(',,,,')
            if len(partes_principais) < 2: continue
            
            cabecalho = partes_principais[0].split(',') # [010000, 1, , ATIVO]
            classificacao = cabecalho[1].strip()
            descricao = cabecalho[3].strip() if len(cabecalho) > 3 else ""

            # BLOCO B: Valores (estão após as 4 vírgulas, separados por 2 vírgulas)
            # O "Saldo Atual" é o último valor da sequência
            bloco_valores = partes_principais[1].split(',,')
            # O Saldo Atual costuma ser o 4º valor (índice 3)
            if len(bloco_valores) >= 4:
                valor_raw = bloco_valores[3].strip().replace(',', '') # Pega o "3,152,485.89d"
                valor_final = self._parse_us_number(valor_raw)

                if classificacao and descricao:
                    nivel = classificacao.count('.') + 1
                    conta_obj = {
                        "classificacao": classificacao,
                        "descricao": descricao.upper(),
                        "valor": valor_final,
                        "nivel": nivel
                    }
                    contas.append(conta_obj)

                    # Organiza as variáveis de Grau 1 (Ativo, Passivo, etc)
                    if nivel == 1:
                        self.grupos_grau_1[classificacao] = {
                            "nome": descricao.upper(),
                            "valor": valor_final
                        }

        return {
            "metadata": self.metadata,
            "resumo_grau_1": self.grupos_grau_1,
            "contas": contas
        }

    def _parse_us_number(self, s):
        """Trata o formato do balancete: 3,152,485.89d"""
        # Já removemos a vírgula de milhar no split anterior
        is_negative = 'C' in s.upper() or '-' in s or '(' in s
        # Remove letras e garante que o ponto decimal permaneça
        clean = re.sub(r'[^\d.]', '', s)
        try:
            return -float(clean) if is_negative else float(clean)
        except: return 0.0