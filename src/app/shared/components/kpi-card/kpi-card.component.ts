import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="containerClass()">
      <p class="text-xs font-bold text-emerald-700 uppercase tracking-widest mb-1">{{ label() }}</p>
      
      <div class="flex items-baseline gap-2">
        <h3 class="text-3xl font-black text-slate-900">{{ formattedValue() }}</h3>
        @if (trend()) {
          <span [class]="trendClass()">{{ trend() }}</span>
        }
      </div>

      <div class="flex items-center gap-1 mt-2">
        @if (isCritical()) {
          <span class="text-[10px] bg-rose-600 text-white px-1.5 py-0.5 rounded font-black uppercase">Crítico</span>
        }
        <p class="text-[10px] text-slate-500 font-medium italic">{{ description() }}</p>
      </div>
    </div>
  `
})
export class KpiCardComponent {
  label = input.required<string>();
  value = input.required<number | string>();
  type = input<'currency' | 'percent' | 'number'>('number');
  trend = input<string>(); 
  description = input<string>('Baseado no último fechamento');

  // Verifica se o índice de Liquidez Corrente está abaixo do limite de segurança (1.0)
  isCritical = computed(() => {
    if (this.label().toLowerCase().includes('liquidez')) {
      return Number(this.value()) <= 1.0;
    }
    return false;
  });

  // Define a classe do container baseada no estado crítico ou normal
  containerClass = computed(() => {
    const base = "p-6 rounded-2xl border-l-8 shadow-sm transition-all duration-300 ";
    return this.isCritical() 
      ? base + "bg-rose-50 border-rose-600 shadow-rose-100" 
      : base + "bg-white border-emerald-600 hover:shadow-md border-y border-r border-emerald-50";
  });

  formattedValue = computed(() => {
    const val = this.value();
    if (typeof val === 'string') return val;
    
    if (this.type() === 'currency') {
      return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
    }
    if (this.type() === 'percent') {
      return `${val.toFixed(2)}%`;
    }
    return val.toFixed(2);
  });

  trendClass = computed(() => {
    const isPositive = this.trend()?.includes('▲');
    return `text-sm font-black ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`;
  });
}