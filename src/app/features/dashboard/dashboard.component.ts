import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { FinancialService } from '../../core/services/financial.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  financialService = inject(FinancialService);
  sanitizer = inject(DomSanitizer);

  selectedFiles = signal<File[]>([]);
  fileYears = signal<Record<string, number>>({});

  orderedYears = computed(() => [...(this.financialService.dashboardData()?.anos_detectados || [])].sort((a, b) => a - b));

  get renderedHtml(): SafeHtml {
    const html = this.financialService.dashboardData()?.html || '';
    return this.sanitizer.bypassSecurityTrustHtml(html);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    this.selectedFiles.set(files);

    const years: Record<string, number> = {};
    files.forEach((file) => {
      const match = file.name.match(/(20\d{2})/);
      years[file.name] = match ? Number(match[1]) : new Date().getFullYear();
    });
    this.fileYears.set(years);
  }

  updateYear(fileName: string, value: string) {
    const next = { ...this.fileYears() };
    next[fileName] = Number(value);
    this.fileYears.set(next);
  }

  generateDashboard() {
    const files = this.selectedFiles();
    if (!files.length) return;
    this.financialService.uploadFiles(files, this.fileYears()).subscribe();
  }

  print() {
    const content = this.financialService.dashboardData()?.html;
    if (!content) return;

    const printWindow = window.open('', '_blank', 'width=1200,height=900');
    if (!printWindow) return;

    printWindow.document.open();
    printWindow.document.write(content);
    printWindow.document.close();

    setTimeout(() => {
      printWindow.focus();
      printWindow.print();
      printWindow.close();
    }, 250);
  }
}
