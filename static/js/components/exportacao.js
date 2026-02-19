export function exportarTabelaCSV(tabela) {
    let csv = "Conta;Anterior;Atual;Variação %;Status\n";
    
    tabela.forEach(row => {
        csv += `${row.conta};${row.anterior};${row.atual};${row.perc};${row.status}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", "analise_emerald.csv");
    link.click();
}