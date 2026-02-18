/**
 * Componente: TabelasComponent
 * Renderiza a listagem unificada de contas sem divisores de texto.
 */
export const TabelasComponent = {
    render: function(dados) {
        const tbody = document.getElementById('comparative-table-body');
        if (!tbody || !dados) return;

        tbody.innerHTML = '';

        const ordens = {
            patrimonial: [
                { label: 'Ativo Circulante', chave: 'ATIVO_CIRCULANTE' },
                { label: 'Ativo Não Circulante', chave: 'ATIVO_NAO_CIRCULANTE' },
                { label: 'Passivo Circulante', chave: 'PASSIVO_CIRCULANTE' },
                { label: 'Passivo Não Circulante', chave: 'PASSIVO_NAO_CIRCULANTE' },
                { label: 'Patrimônio Líquido', chave: 'PATRIMONIO_LIQUIDO' }
            ],
            resultado: [
                { label: 'Receita Bruta', chave: 'RECEITA_BRUTA' },
                { label: 'Receita Líquida', chave: 'RECEITA_LIQ' },
                { label: 'Lucro Bruto', chave: 'LUCRO_BRUTO' },
                { label: 'Despesas Operacionais', chave: 'DESP_OP' },
                { label: 'EBITDA', chave: 'EBITDA' },
                { label: 'Lucro Líquido', chave: 'LUCRO_LIQ' }
            ]
        };

        const criarLinha = (label, chave, fonte) => {
            if (!fonte) return '';
            const vAnt = fonte[`${chave}_ANT`] || 0;
            const vAtu = fonte[`${chave}_ATUAL`] || 0;
            const perc = fonte[`${chave}_PERC`] || 0;
            const status = fonte[`${chave}_STATUS`] || '';
            
            const color = perc < 0 ? 'text-rose-500' : 'text-emerald-500';
            const icon = status.split(' ')[0] || (perc < 0 ? '▼' : '▲');

            return `
                <tr class="hover:bg-slate-50 border-b border-slate-100 transition-colors">
                    <td class="py-3 px-2 font-medium text-slate-700 text-sm">${label}</td>
                    <td class="py-3 px-2 text-right text-slate-500 tabular-nums">${this.f(vAnt)}</td>
                    <td class="py-3 px-2 text-right font-bold text-slate-900 tabular-nums">${this.f(vAtu)}</td>
                    <td class="py-3 px-2 text-right font-bold ${color} tabular-nums">
                        <span class="text-[10px] mr-1 opacity-70">${icon}</span>${Math.abs(perc).toFixed(2)}%
                    </td>
                </tr>`;
        };

        const fonteBalancete = dados.balancete?.placeholders || dados.balancete || {};
        const fonteDre = dados.dre?.placeholders || dados.dre || {};

        let html = '';
        
        // Renderiza Patrimonial 
        ordens.patrimonial.forEach(item => {
            html += criarLinha(item.label, item.chave, fonteBalancete);
        });

        // Renderiza Resultado na sequência, sem separador 
        ordens.resultado.forEach(item => {
            html += criarLinha(item.label, item.chave, fonteDre);
        });

        tbody.innerHTML = html;
    },

    f: (v) => new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v)
};