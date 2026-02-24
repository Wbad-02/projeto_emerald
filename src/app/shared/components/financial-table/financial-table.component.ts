import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TableRow } from '../../../core/model/financial.model';

@Component({
  selector: 'app-financial-table',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="overflow-hidden rounded-lg border border-emerald-100 bg-white shadow-sm">
      <table class="w-full text-left text-sm">
        <thead class="bg-emerald-900 text-white uppercase text-[10px] font-bold">
          <tr>
            <th class="px-6 py-4">Conta</th>
            <th class="px-6 py-4 text-right">Anterior</th>
            <th class="px-6 py-4 text-right">Atual</th>
            <th class="px-6 py-4 text-center">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-emerald-50">
          @for (row of data; track row.conta) {
            <tr class="hover:bg-emerald-50/50 transition-colors">
              <td class="px-6 py-4 font-medium text-slate-700">{{ row.conta }}</td>
              <td class="px-6 py-4 text-right text-slate-500">{{ row.anterior | currency:'BRL' }}</td>
              <td class="px-6 py-4 text-right font-bold text-slate-900">{{ row.atual | currency:'BRL' }}</td>
              <td class="px-6 py-4 text-center">
                <span class="px-2 py-1 rounded text-[10px] font-bold uppercase"
                  [ngClass]="row.status.includes('Crescimento') ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'">
                  {{ row.status }} ({{ row.perc }}%)
                </span>
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `
})
export class FinancialTableComponent {
  @Input({ required: true }) data: TableRow[] = [];
}