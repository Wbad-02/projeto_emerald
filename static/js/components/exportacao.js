const ExportadorPDF = {
    imprimir: function() {
        document.body.classList.add('printing-mode');
        // Força o Chart.js a se ajustar
        window.dispatchEvent(new Event('resize'));
        window.print();
        document.body.classList.remove('printing-mode');
    }
};
// Torna global para usar no HTML
window.ExportadorPDF = ExportadorPDF;