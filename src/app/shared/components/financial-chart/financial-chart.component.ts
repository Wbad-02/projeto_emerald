import { Component, Input, OnInit, ViewChild, ElementRef, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-financial-chart',
  standalone: true,
  template: `<div class="relative h-[300px] w-full">
               <canvas #chartCanvas></canvas>
             </div>`,
  styles: [`:host { display: block; width: 100%; }`]
})
export class FinancialChartComponent implements OnInit {
  @ViewChild('chartCanvas', { static: true }) chartCanvas!: ElementRef;
  @Input({ required: true }) config!: ChartConfiguration;
  
  private platformId = inject(PLATFORM_ID);

  ngOnInit() {
    // Garante que o gráfico só renderize no navegador (evita erros de SSR)
    if (isPlatformBrowser(this.platformId)) {
      new Chart(this.chartCanvas.nativeElement, this.config);
    }
  }
}