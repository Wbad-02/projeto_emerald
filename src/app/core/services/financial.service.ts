import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs'; // Adicionado
import { FinancialResponse, TableRow } from '../model/financial.model';

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

  // Alterado para retornar Observable e usar o operador tap
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