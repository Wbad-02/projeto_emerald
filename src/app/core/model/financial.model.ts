export interface TableRow {
  conta: string;
  anterior: number;
  atual: number;
  perc: number;
  status: string;
}

export interface ComparativeYearRow {
  conta: string;
  tipo: 'Patrimonial' | 'DRE';
  valores: Record<string, number | null>;
}

export interface Recommendation {
  texto: string;
  valor: number;
}

export interface TaxRegime {
  nome: string;
  valor: number;
  economica: boolean;
}

// ETAPA 5: Interface para os Gráficos de BI [cite: 5, 8, 34]
export interface FinancialCharts {
  composicao_ativo: { name: string, value: number }[];
  composicao_passivo: { name: string, value: number }[];
  evolucao_patrimonial: {
    categorias: string[];
    anterior: number[];
    atual: number[];
  };
  dre: { name: string, valor: number }[];
}

export interface FinancialResponse {
  empresa: string;
  anos: Record<string, any>;
  indices: Record<string, any>;
  tabela_patrimonial: TableRow[];
  tabela_dre: TableRow[];
  comparativo_tributario: TaxRegime[];
  recomendacao?: { texto: string; valor: number };
  // Adicionado para suportar a Análise Visual (BI)
  graficos: FinancialCharts;
}
