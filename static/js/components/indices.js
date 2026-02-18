export const IndicesComponent = {
    render: function(dados) {
        if (!dados || !dados.dre) return;

        const p = dados.dre.placeholders || dados.dre;
        const b = dados.balancete?.placeholders || dados.balancete || {};
        const i = dados.indices || {};

        // --- DADOS PARA OS NOVOS CARDS ---
        const receita = p.RECEITA_BRUTA_ATUAL || 0;
        const lucro = p.LUCRO_LIQ_ATUAL || 0;
        const lucroBruto = p.LUCRO_BRUTO_ATUAL || 0;
        const ativoTotal = b.ATIVO_CIRCULANTE_ATUAL + b.ATIVO_NAO_CIRCULANTE_ATUAL || 1;

        // Cálculos de Rentabilidade
        const margemLiquida = receita > 0 ? (lucro / receita) * 100 : 0;
        const margemBruta = receita > 0 ? (lucroBruto / receita) * 100 : 0;
        const roa = (lucro / ativoTotal) * 100;

        // --- RENDERIZAÇÃO DOS CARDS EXISTENTES ---
        this.updateCard('card-liquidez', i.liq_corrente?.toFixed(2), this.regraLiquidez(i.liq_corrente));
        this.updateCard('card-endividamento', i.endiv_geral?.toFixed(2) + '%', this.regraEndividamento(i.endiv_geral));
        this.updateCard('card-receita', this.f(receita));
        this.updateCard('card-lucro', this.f(lucro));

        // --- RENDERIZAÇÃO DOS NOVOS CARDS (ETAPA 4) ---
        this.updateCard('card-margem-liq', margemLiquida.toFixed(2) + '%', this.regraMargem(margemLiquida));
        this.updateCard('card-margem-bruta', margemBruta.toFixed(2) + '%', this.regraMargem(margemBruta));
        this.updateCard('card-roa', roa.toFixed(2) + '%', this.regraROA(roa));
    },

    // Regras de Cor e Status
    regraLiquidez: (v) => v > 1.5 ? {txt: '✅ Ótima capacidade', cor: 'positive'} : v >= 1 ? {txt: '⚠️ Capacidade ajustada', cor: 'neutral'} : {txt: '❌ Risco de solvência', cor: 'negative'},
    
    regraEndividamento: (v) => v < 50 ? {txt: '✅ Baixo endividamento', cor: 'positive'} : v <= 70 ? {txt: '⚠️ Atenção ao passivo', cor: 'neutral'} : {txt: '❌ Endividamento alto', cor: 'negative'},
    
    regraMargem: (v) => v > 10 ? {txt: '✅ Alta rentabilidade', cor: 'positive'} : v >= 5 ? {txt: '⚠️ Margem média', cor: 'neutral'} : {txt: '❌ Margem estreita', cor: 'negative'},

    regraROA: (v) => v > 5 ? {txt: '✅ Uso eficiente do Ativo', cor: 'positive'} : {txt: '⚠️ Retorno moderado', cor: 'neutral'},

    updateCard: function(id, valor, status) {
        const el = document.getElementById(id);
        if (!el) return;
        const valEl = el.querySelector('.value');
        const statusEl = el.querySelector('.status-text');
        
        if (valEl) valEl.innerText = valor;
        if (statusEl && status) {
            statusEl.innerText = status.txt;
            // Mapeia as cores para classes Tailwind
            const cores = {
                positive: 'text-emerald-600',
                neutral: 'text-amber-600',
                negative: 'text-rose-600'
            };
            statusEl.className = `status-text text-[11px] font-bold mt-2 ${cores[status.cor]}`;
        }
    },

    f: (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)
};