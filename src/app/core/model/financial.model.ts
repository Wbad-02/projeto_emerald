export interface TableRow {
  conta: string;
  anterior: number;
  atual: number;
  perc: number;
  status: string;
}

export interface DashboardGenerateResponse {
  html: string;
  placeholders: Record<string, unknown>;
  anos_detectados: number[];
  warnings: string[];
}
