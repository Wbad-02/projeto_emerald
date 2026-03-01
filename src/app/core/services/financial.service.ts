import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { DashboardGenerateResponse } from '../model/financial.model';

@Injectable({ providedIn: 'root' })
export class FinancialService {
  private http = inject(HttpClient);
  private readonly apiUrl = '/api/dashboard/generate';

  dashboardData = signal<DashboardGenerateResponse | null>(null);
  isLoading = signal(false);

  uploadFiles(files: File[], fileYears: Record<string, number>): Observable<DashboardGenerateResponse> {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    formData.append('file_years', JSON.stringify(fileYears));

    this.isLoading.set(true);
    return this.http.post<DashboardGenerateResponse>(this.apiUrl, formData).pipe(
      tap({
        next: (res) => {
          this.dashboardData.set(res);
          this.isLoading.set(false);
        },
        error: () => this.isLoading.set(false),
      })
    );
  }
}