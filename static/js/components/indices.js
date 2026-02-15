/**
 * Atualiza os cards de indicadores com base nos parâmetros da Tabela 3
 */
export function updateIndices(indices, dre) {
    const formatador = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

    // 1. Configuração dos Cards baseados no objeto 'indices' (Balancete)
    const configCards = [
        {
            id: 'card-liq-corrente',
            valor: indices?.liq_corrente || 0,
            prefixo: '',
            sufixo: '',
            // Tabela 3: < 1.0 (Crítico), 1.0-1.5 (Atenção), > 1.5 (Bom)
            cor: (v) => v < 1.0 ? 'text-red-600' : (v < 1.5 ? 'text-amber-500' : 'text-emerald-600')
        },
        {
            id: 'card-endividamento',
            valor: indices?.endiv_geral || 0,
            prefixo: '',
            sufixo: '%',
            // Tabela 3: > 70% (Crítico), 50-70% (Atenção), < 50% (Saudável)
            cor: (v) => v > 70 ? 'text-red-600' : (v > 50 ? 'text-amber-500' : 'text-emerald-600')
        },
        {
            id: 'card-margem-liquida',
            valor: indices?.margem_liq || 0,
            prefixo: '',
            sufixo: '%',
            // Tabela 3: < 0% (Crítico), 0-5% (Baixa), > 5% (Adequada)
            cor: (v) => v < 0 ? 'text-red-600' : (v < 5 ? 'text-amber-500' : 'text-emerald-600')
        }
    ];

    configCards.forEach(card => {
        const el = document.getElementById(card.id);
        if (el) {
            el.innerText = `${card.prefixo}${card.valor.toFixed(2)}${card.sufixo}`;
            el.className = `text-3xl font-black ${card.cor(card.valor)}`;
        }
    });

    // 2. Atualização dos Cards baseados no objeto 'dre' (DRE)
    // Blindagem: evita o erro "Cannot read properties of undefined"
    if (!dre) {
        console.warn("Aviso: Dados da DRE não foram recebidos corretamente.");
        return;
    }

    const recEl = document.getElementById('card-receita-atual');
    const lucEl = document.getElementById('card-lucro-atual');

    if (recEl) {
        // Usa valor 0 como fallback caso a chave não exista
        recEl.innerText = formatador.format(dre.RECEITA_BRUTA_ATUAL || 0);
    }

    if (lucEl) {
        const valorLucro = dre.LUCRO_LIQ_ATUAL || 0;
        lucEl.innerText = formatador.format(valorLucro);
        // Aplica cor conforme Tabela 3: < 0 (Prejuízo/Crítico)
        lucEl.className = `text-3xl font-black ${valorLucro < 0 ? 'text-red-600' : 'text-emerald-600'}`;
    }
}