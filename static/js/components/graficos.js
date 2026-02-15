let chartInstance = null;

export function renderCharts(dre) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Receita Líquida', 'Lucro Bruto', 'Despesas Operacionais'],
            datasets: [{
                label: 'Valores (R$)',
                data: [
                    Math.abs(dre.RECEITA_LIQ_ATUAL),
                    Math.abs(dre.LUCRO_BRUTO_ATUAL),
                    Math.abs(dre.DESP_OP_ATUAL)
                ],
                backgroundColor: ['#10b981', '#34d399', '#ef4444'],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}