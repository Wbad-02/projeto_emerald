import re

class FinanceFormatter:
    @staticmethod
    def clean_value(val, is_balancete=False):
        if not val or str(val).lower() == 'nan': return 0.0
        s = str(val).strip().lower()
        is_negative = '(' in s or '-' in s
        
        # Balancete Itasul usa ponto para decimal: 1,234.56
        # DRE Itasul usa vírgula para decimal: 1.234,56
        if is_balancete:
            s = re.sub(r'[^\d.]', '', s.replace(',', ''))
        else:
            s = re.sub(r'[^\d,]', '', s.replace('.', '')).replace(',', '.')
            
        try:
            num = float(s)
            return -num if is_negative else num
        except: return 0.0