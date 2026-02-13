/**
 * Renderiza a Tabela de Análise Comparativa conforme a referência
 */
export function renderizarAnaliseComparativa(comparativo) {
    const tbody = document.getElementById('comparative-table-body');
    if (!tbody) return;

    tbody.innerHTML = ''; 

    comparativo.forEach(item => {
        const isPositivo = item.variacao >= 0;
        const corTexto = isPositivo ? 'text-emerald-600' : 'text-red-600';
        const sinal = isPositivo ? '↑' : '↓';
        const labelStatus = isPositivo ? 'Crescimento' : 'Queda';

        const row = `
            <tr class="border-b hover:bg-gray-50 transition-colors">
                <td class="p-4 font-semibold text-gray-700">${item.conta}</td>
                <td class="p-4 text-right text-gray-600">${formatarMoeda(item.anterior)}</td>
                <td class="p-4 text-right text-gray-600">${formatarMoeda(item.atual)}</td>
                <td class="p-4 text-right font-bold ${corTexto}">
                    ${isPositivo ? '+' : ''}${formatarMoeda(item.variacao)}
                </td>
                <td class="p-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                        isPositivo 
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-700' 
                        : 'bg-red-50 border-red-200 text-red-700'
                    }">
                        ${sinal} ${labelStatus} (${Math.abs(item.status_percentual).toFixed(1)}%)
                    </span>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

/**
 * Renderiza o Detalhamento Geral (Tabela Inferior)
 */
export function renderizarDetalhamento(dadosAno) {
    const container = document.getElementById('tabela-container');
    if (!container) return;

    // Une as contas para exibição detalhada
    const contas = [
        ...(dadosAno.balancete ? dadosAno.balancete.contas : []),
        ...(dadosAno.dre ? dadosAno.dre.contas : [])
    ];

    let html = '<table class="w-full text-left border-collapse text-sm">';
    contas.forEach(c => {
        const indent = (c.nivel - 1) * 16;
        html += `
            <tr class="border-b hover:bg-emerald-50 ${c.nivel === 1 ? 'bg-gray-50 font-bold' : ''}">
                <td class="p-3" style="padding-left: ${indent + 12}px">${c.descricao}</td>
                <td class="p-3 text-right font-mono">${formatarMoeda(c.valor)}</td>
            </tr>`;
    });
    html += '</table>';
    container.innerHTML = html;
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}