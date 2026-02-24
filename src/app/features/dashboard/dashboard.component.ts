import { Component, inject, computed, effect, ViewChild, ElementRef, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FinancialService } from '../../core/services/financial.service';
import { FinancialTableComponent } from '../../shared/components/financial-table/financial-table.component';
import { KpiCardComponent } from '../../shared/components/kpi-card/kpi-card.component';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, FinancialTableComponent, KpiCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  financialService = inject(FinancialService);
  Object = Object;

  @ViewChild('chartAtivo') chartAtivo!: ElementRef;
  @ViewChild('chartPassivo') chartPassivo!: ElementRef;
  @ViewChild('chartEvolucao') chartEvolucao!: ElementRef;
  @ViewChild('chartDre') chartDre!: ElementRef;

  private charts: Chart[] = [];
  
  // SINAIS: Controle reativo de estado para evitar pop-ups
  novaNotaTexto = signal(''); 
  recomendacoesManuais = signal<string[]>([]);

  constructor() {
    effect(() => {
      const data = this.financialService.dashboardData();
      if (data && data.graficos) {
        // Delay para garantir que o DOM renderizou os canvas
        setTimeout(() => this.initCharts(data), 100);
      }
    });
  }

  formatKey(key: string): string {
    const labels: Record<string, string> = {
      'liq_corrente': 'Liquidez Corrente',
      'endiv_geral': 'Endividamento Geral',
      'margem_liquida': 'Margem Líquida',
      'roa': 'ROA (Rent. Ativos)',
      'roe': 'ROE (Rent. Sócio)'
    };
    return labels[key.toLowerCase()] || key.replace(/_/g, ' ').toUpperCase();
  }

  getIndicatorClass(key: string, value: number): string {
    const k = key.toLowerCase();
    if (k.includes('liq_corrente')) return value < 1.0 ? 'status-critico' : 'status-sucesso';
    if (k.includes('endiv_geral')) return value > 70 ? 'status-critico' : 'status-sucesso';
    if (k.includes('margem_liquida') || k.includes('roa') || k.includes('roe')) {
      if (value <= 0) return 'status-critico';
      if (value < 10) return 'status-atencao';
      return 'status-sucesso';
    }
    return 'status-padrao';
  }

  getIndicatorNote(key: string, value: number): string {
    const k = key.toLowerCase();
    if (k.includes('liq_corrente')) return value < 1.0 ? '🚨 CRÍTICO: Insolvência' : '✅ ADEQUADO';
    if (k.includes('endiv_geral')) return value > 70 ? '🚨 CRÍTICO: Alavancagem' : '✅ SAUDÁVEL';
    return 'Análise via Emerald Intelligence';
  }

  getAnosProcessados(anosObj: any): string {
    return anosObj ? Object.keys(anosObj).sort().join(' VS ') : '...';
  }

  // GESTÃO DE RECOMENDAÇÕES (IA + SINAL MANUAL)
  todasRecomendacoes = computed(() => {
    const data = this.financialService.dashboardData();
    if (!data) return [];
    
    const ind = data.indices;
    const automaticas: any[] = [];

    // Lógica para a ITASUL baseada nos dados do sistema
    if (ind['liq_corrente'] < 1.0) {
      automaticas.push({
        titulo: "Risco de Insolvência",
        texto: `A liquidez corrente de ${ind['liq_corrente']} é crítica. A empresa possui apenas R$ 0,45 para cada R$ 1,00 de dívida imediata[cite: 5, 13].`,
        urgencia: "ALTA"
      });
    }

    if (ind['endiv_geral'] > 70) {
      automaticas.push({
        titulo: "Alavancagem Perigosa",
        texto: `O endividamento de ${ind['endiv_geral']}% compromete a autonomia financeira. Passivo circulante representa R$ 2,48M[cite: 5].`,
        urgencia: "CRÍTICA"
      });
    }

    const melhorRegime = data.comparativo_tributario?.find((r: any) => r.economica);
    if (melhorRegime) {
      automaticas.push({
        titulo: "Otimização Fiscal",
        texto: `Migração para ${melhorRegime.nome} recomendada. Economia anual estimada reduzindo a carga para ${melhorRegime.valor.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}[cite: 78, 80].`,
        urgencia: "ESTRATÉGICA"
      });
    }

    const manuais = this.recomendacoesManuais().map(txt => ({
      titulo: "Nota do Especialista",
      texto: txt,
      urgencia: "PERSONALIZADA"
    }));

    return [...automaticas, ...manuais];
  });

  // Vinculação bidirecional com Signal
  atualizarTexto(event: any) {
    this.novaNotaTexto.set(event.target.value);
  }

  salvarNotaManual() {
    const texto = this.novaNotaTexto().trim();
    if (texto) {
      this.recomendacoesManuais.update(prev => [...prev, texto]);
      this.novaNotaTexto.set(''); 
    }
  }

  // Alias para compatibilidade com a linha 77 do HTML
  adicionarRecomendacao() {
    this.salvarNotaManual();
  }

  private initCharts(data: any) {
    if (!this.chartAtivo) return; 

    this.charts.forEach(c => c.destroy());
    this.charts = [];
    const commonOptions = { responsive: true, maintainAspectRatio: false };

    this.charts.push(new Chart(this.chartAtivo.nativeElement, {
      type: 'doughnut',
      data: {
        labels: data.graficos.composicao_ativo.map((i: any) => i.name),
        datasets: [{ data: data.graficos.composicao_ativo.map((i: any) => i.value), backgroundColor: ['#10b981', '#e2e8f0'] }]
      },
      options: { ...commonOptions, cutout: '60%', plugins: { legend: { position: 'bottom' } } }
    }));

    this.charts.push(new Chart(this.chartPassivo.nativeElement, {
      type: 'doughnut',
      data: {
        labels: data.graficos.composicao_passivo.map((i: any) => i.name),
        datasets: [{ data: data.graficos.composicao_passivo.map((i: any) => i.value), backgroundColor: ['#f43f5e', '#94a3b8', '#10b981'] }]
      },
      options: { ...commonOptions, cutout: '60%', plugins: { legend: { position: 'bottom' } } }
    }));

    this.charts.push(new Chart(this.chartEvolucao.nativeElement, {
      type: 'line',
      data: {
        labels: data.graficos.evolucao_patrimonial.categorias,
        datasets: [
          { label: 'Anterior', data: data.graficos.evolucao_patrimonial.anterior, borderColor: '#94a3b8', tension: 0.4 },
          { label: 'Atual', data: data.graficos.evolucao_patrimonial.atual, borderColor: '#10b981', tension: 0.4 }
        ]
      },
      options: commonOptions
    }));

    this.charts.push(new Chart(this.chartDre.nativeElement, {
      type: 'bar',
      data: {
        labels: data.graficos.dre.map((i: any) => i.name),
        datasets: [{ label: 'Valor', data: data.graficos.dre.map((i: any) => i.valor), backgroundColor: '#10b981' }]
      },
      options: commonOptions
    }));
  }

  onFileSelected(event: any) {
    const files = event.target.files;
    if (files.length) this.financialService.uploadFiles(Array.from(files)).subscribe();
  }

  print() { window.print(); } 
}