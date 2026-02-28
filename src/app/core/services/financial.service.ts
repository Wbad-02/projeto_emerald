import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { ComparativeYearRow, FinancialResponse, TableRow } from '../model/financial.model';

@Injectable({ providedIn: 'root' })
export class FinancialService {
  private http = inject(HttpClient);
  private readonly apiUrl = 'http://127.0.0.1:5000/processar';

  dashboardData = signal<FinancialResponse | null>(null);
  isLoading = signal(false);

  unifiedTable = computed<TableRow[]>(() => {
    const data = this.dashboardData();
    if (!data) return [];
    return [
      ...data.tabela_patrimonial,
      ...data.tabela_dre
    ];
  });

  anosOrdenados = computed<string[]>(() => {
    const data = this.dashboardData();
    if (!data?.anos) return [];
    return Object.keys(data.anos).sort((a, b) => Number(a) - Number(b));
  });

  comparativeYearTable = computed<ComparativeYearRow[]>(() => {
    const data = this.dashboardData();
    const anos = this.anosOrdenados();
    if (!data?.anos || !anos.length) return [];

    const tableMap = new Map<string, ComparativeYearRow>();

    const upsert = (tipo: 'Patrimonial' | 'DRE', conta: string, ano: string, valor: number) => {
      const key = `${tipo}::${conta}`;
      const existing = tableMap.get(key) ?? {
        conta,
        tipo,
        valores: Object.fromEntries(anos.map((a) => [a, null]))
      };

      existing.valores[ano] = Number.isFinite(valor) ? valor : 0;
      tableMap.set(key, existing);
    };

    for (const ano of anos) {
      const dadosAno = data.anos[ano] ?? {};
      const patrimonial = dadosAno?.balancete?.resumo_grau_1 ?? {};
      const dre = dadosAno?.dre?.indicadores_grau_1 ?? {};

      for (const [conta, valor] of Object.entries(patrimonial)) {
        upsert('Patrimonial', conta, ano, Number(valor));
      }

      for (const [conta, valor] of Object.entries(dre)) {
        upsert('DRE', conta, ano, Number(valor));
      }
    }

    return Array.from(tableMap.values()).sort((a, b) => {
      if (a.tipo !== b.tipo) {
        return a.tipo.localeCompare(b.tipo);
      }
      return a.conta.localeCompare(b.conta);
    });
  });

  uploadFiles(files: File[]): Observable<FinancialResponse> {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

    this.isLoading.set(true);

    return this.http.post<FinancialResponse>(this.apiUrl, formData).pipe(
      tap({
        next: (res) => {
          this.dashboardData.set(res);
          this.isLoading.set(false);
        },
        error: () => this.isLoading.set(false)
      })
    );
  }
}
