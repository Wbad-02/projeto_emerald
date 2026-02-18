/**
 * Componente: GraficosComponent
 * Versão simplificada contendo apenas os gráficos 2, 3, 4 e 5.
 */
export const GraficosComponent = {
    instances: {},

    render: function(dados) {
        if (!dados || !dados.indices) return;
        const p = dados.indices;

        // Função auxiliar robusta para buscar chaves curtas ou longas
        const getV = (curta, longa) => p[curta] || p[longa] || 0;

        // 2 - Composição do Ativo (Rosca)
        this.renderRosca('ativoChart', ['Circulante', 'Não Circulante'], 
            [getV('ATIVO_CIRCULANTE_ATUAL', 'ATIVO_CIRCULANTE_ATUAL'), getV('ATIVO_NAO_CIRCULANTE_ATUAL', 'ATIVO_NAO_CIRCULANTE_ATUAL')], 
            ['#10b981', '#34d399']);
        
        // 3 - Composição do Passivo (Rosca)
        this.renderRosca('passivoChart', ['Circulante', 'Não Circulante', 'PL'], 
            [
                getV('PASSIVO_CIRCULANTE_ATUAL', 'PASSIVO_CIRCULANTE_ATUAL'), 
                getV('PASSIVO_NAO_CIRCULANTE_ATUAL', 'PASSIVO_NAO_CIRCULANTE_ATUAL'), 
                getV('PATRIMONIO_LIQUIDO_ATUAL', 'PATRIMONIO_LIQUIDO_ATUAL')
            ], 
            ['#f43f5e', '#fb7185', '#94a3b8']);

        // 4 - Evolução Patrimonial (Linha)
        this.renderEvolucao('evolucaoChart', dados.anos, {
            'Ativo Total': [p.ATIVO_TOTAL_ANT || 0, p.ATIVO_TOTAL_ATUAL || 0],
            'Passivo Total': [p.PASSIVO_TOTAL_ANT || 0, p.PASSIVO_TOTAL_ATUAL || 0],
            'PL': [p.PATRIMONIO_LIQUIDO_ANT || 0, p.PATRIMONIO_LIQUIDO_ATUAL || 0]
        });

        // 5 - DRE (Barras)
        this.renderDRE('dreChart', 
            ['Receita Líquida', 'Lucro Bruto', 'Lucro Líquido'],
            [p.RECEITA_LIQ_ATUAL || 0, p.LUCRO_BRUTO_ATUAL || 0, p.LUCRO_LIQ_ATUAL || 0]);
    },

    // --- MÉTODOS DE DESENHO REMANESCENTES ---

    renderRosca: function(id, labels, data, colors) {
        const ctx = document.getElementById(id);
        if (!ctx) return;
        this.destroy(id);
        this.instances[id] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{ data: data, backgroundColor: colors, borderWidth: 0 }]
            },
            options: { cutout: '70%', responsive: true, maintainAspectRatio: false }
        });
    },

    renderEvolucao: function(id, anos, datasets) {
        const ctx = document.getElementById(id);
        if (!ctx) return;
        this.destroy(id);
        const colors = ['#6366f1', '#f43f5e', '#10b981'];
        this.instances[id] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: anos || ['Anterior', 'Atual'],
                datasets: Object.keys(datasets).map((key, i) => ({
                    label: key, data: datasets[key], borderColor: colors[i], tension: 0.3, fill: false
                }))
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    },

    renderDRE: function(id, labels, data) {
        const ctx = document.getElementById(id);
        if (!ctx) return;
        this.destroy(id);
        this.instances[id] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{ label: 'Valor Atual', data: data, backgroundColor: '#3b82f6', borderRadius: 5 }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    },

    destroy: function(id) {
        if (this.instances[id]) this.instances[id].destroy();
    }
};