export const RegimesComponent = {
    render: function(dados) {
        const container = document.getElementById('regime-results');
        if (!container || !dados.indices) return;

        const rb = dados.indices.RECEITA_BRUTA_ATUAL || 0;
        const ll = dados.indices.LUCRO_LIQ_ATUAL || 0;

        // Cálculos Simplificados baseados no PDF de exemplo [cite: 71, 72, 73]
        const simples = rb * 0.12; // Alíquota média 12%
        const presumido = (rb * 0.059) + (ll * 0.05); // IRPJ/CSLL Presumido + PIS/COFINS (Simulado)
        const real = ll * 0.34; // IRPJ/CSLL 34% sobre Lucro Real

        const regimes = [
            { nome: 'Simples Nacional', valor: simples, desc: 'Ideal para faturamento até R$ 4,8mi' },
            { nome: 'Lucro Presumido', valor: presumido, desc: 'Recomendado para faturamento até R$ 78mi' },
            { nome: 'Lucro Real', valor: real, desc: 'Obrigatório para grandes volumes ou margens baixas' }
        ];

        // Ordenar para encontrar o mais vantajoso [cite: 61]
        regimes.sort((a, b) => a.valor - b.valor);

        container.innerHTML = regimes.map((r, i) => `
            <div class="${i === 0 ? 'bg-emerald-600 scale-105 shadow-xl' : 'bg-slate-700'} p-6 rounded-2xl transition-all border border-slate-600">
                <p class="text-[10px] font-bold uppercase opacity-70">${r.nome}</p>
                <p class="text-2xl font-black mt-1">R$ ${r.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</p>
                <p class="text-xs mt-4 opacity-80">${r.desc}</p>
                ${i === 0 ? '<span class="mt-2 inline-block bg-white text-emerald-700 text-[10px] font-black px-2 py-1 rounded">RECOMENDADO</span>' : ''}
            </div>
        `).join('');
    }
};