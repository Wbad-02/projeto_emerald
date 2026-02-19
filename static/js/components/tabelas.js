const formatar = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);

export function renderizarAnaliseComparativa(comparativo) {
    const tbody = document.getElementById('comparative-table-body');
    if (!tbody) return;
    tbody.innerHTML = comparativo.map(item => `
        <tr class="border-b hover:bg-gray-50">
            <td class="p-4 font-semibold text-gray-700">${item.conta}</td>
            <td class="p-4 text-right">${formatar(item.anterior)}</td>
            <td class="p-4 text-right">${formatar(item.atual)}</td>
            <td class="p-4 text-right ${item.perc >= 0 ? 'text-emerald-600' : 'text-red-600'} font-bold">
                ${item.status.split(' ')[0]} ${item.perc}%
            </td>
        </tr>
    `).join('');
}

export function renderizarDetalhamento(dadosAno) {
    const container = document.getElementById('tabela-container');
    if (!container) return;
    const contas = [...(dadosAno.balancete?.contas || []), ...(dadosAno.dre?.contas || [])];
    container.innerHTML = `<table class="w-full text-sm">
        ${contas.map(c => `
            <tr class="border-b ${c.nivel === 1 ? 'bg-gray-50 font-bold' : ''}">
                <td class="p-2" style="padding-left: ${c.nivel * 12}px">${c.descricao}</td>
                <td class="p-2 text-right">${formatar(c.valor)}</td>
            </tr>
        `).join('')}
    </table>`;
}