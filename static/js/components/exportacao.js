document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btn-exportar-pdf');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const content = document.getElementById('dashboard-content');
        if (!content || content.classList.contains('hidden')) {
            alert("Processe os documentos antes de exportar o PDF.");
            return;
        }

        // UI Feedback
        const originalContent = btn.innerHTML;
        btn.innerText = "Gerando PDF...";
        btn.disabled = true;

        // Opções para manter a fidelidade visual idêntica à tela
        const opt = {
            margin: [10, 5, 10, 5], // Margens equilibradas (Topo, Esquerda, Baixo, Direita)
            filename: 'Analise_Financeira_Upgrade.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { 
                scale: 2, // Aumenta a nitidez
                useCORS: true, 
                letterRendering: true,
                scrollY: -window.scrollY, // Resolve problemas de deslocamento se a página estiver com scroll
                windowWidth: document.documentElement.offsetWidth, // Mantém a largura real da tela
                onclone: (clonedDoc) => {
                    // Esconde apenas o que não deve sair no documento final
                    const areaInput = clonedDoc.getElementById('area-input-especialista');
                    const uploadSection = clonedDoc.getElementById('upload-section');
                    const btnExportar = clonedDoc.getElementById('btn-exportar-pdf');
                    
                    if (areaInput) areaInput.style.display = 'none';
                    if (uploadSection) uploadSection.style.display = 'none';
                    if (btnExportar) btnExportar.style.display = 'none';

                    // Garante que o dashboard clonado herde todos os estilos da tela
                    const dashboard = clonedDoc.getElementById('dashboard-content');
                    dashboard.style.display = 'block';
                    dashboard.style.padding = '10px';
                }
            },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait', compress: true },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        };

        // Geração do PDF
        html2pdf().set(opt).from(content).toPdf().get('pdf').then(function (pdf) {
            // Adiciona numeração de página se desejar (opcional)
            const totalPages = pdf.internal.getNumberOfPages();
            for (let i = 1; i <= totalPages; i++) {
                pdf.setPage(i);
                pdf.setFontSize(8);
                pdf.setTextColor(150);
                pdf.text('Página ' + i + ' de ' + totalPages, pdf.internal.pageSize.getWidth() - 30, pdf.internal.pageSize.getHeight() - 5);
            }
        }).save().then(() => {
            btn.innerHTML = originalContent;
            btn.disabled = false;
        });
    });
});