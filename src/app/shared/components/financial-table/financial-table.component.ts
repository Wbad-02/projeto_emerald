import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComparativeYearRow } from '../../../core/model/financial.model';

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
            @for (ano of anos; track ano) {
              <th class="px-6 py-4 text-right">{{ ano }}</th>
            }
          </tr>
        </thead>
        <tbody class="divide-y divide-emerald-50">
          @for (row of data; track row.tipo + '::' + row.conta) {
            <tr class="hover:bg-emerald-50/50 transition-colors">
              <td class="px-6 py-4 font-medium text-slate-700">
                <div class="flex items-center gap-2">
                  <span class="text-[9px] px-2 py-1 rounded bg-slate-100 text-slate-500 font-black uppercase">{{ row.tipo }}</span>
                  <span>{{ row.conta }}</span>
                </div>
              </td>
              @for (ano of anos; track ano) {
                <td class="px-6 py-4 text-right font-bold text-slate-900">
                  @if (row.valores[ano] !== null) {
                    {{ row.valores[ano] | currency:'BRL' }}
                  } @else {
                    <span class="text-slate-400 font-medium">—</span>
                  }
                </td>
              }
            </tr>
          }
        </tbody>
      </table>
    </div>
  `
})
export class FinancialTableComponent {
  @Input({ required: true }) data: ComparativeYearRow[] = [];
  @Input({ required: true }) anos: string[] = [];
}
