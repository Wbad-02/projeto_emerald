import { renderizarAnaliseComparativa, renderizarDetalhamento } from './components/tabelas.js';

document.addEventListener('DOMContentLoaded', () => {
    // Escuta o evento de conclusão do upload
    window.addEventListener('dados-prontos', (e) => {
        const data = e.detail;
        
        // Exibe o dashboard e esconde o upload
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';
        
        // Renderiza a tabela de 5 colunas conforme image_873390.png
        if (data.comparativo) {
            renderizarAnaliseComparativa(data.comparativo);
        }

        // Renderiza o detalhamento do último ano
        const anos = Object.keys(data.anos).sort();
        const ultimoAno = anos[anos.length - 1];
        renderizarDetalhamento(data.anos[ultimoAno]);
    });
});