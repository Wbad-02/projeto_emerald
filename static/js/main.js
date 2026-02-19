import { handleUpload } from './components/upload.js';
import { updateIndices } from './components/indices.js';
import { renderCharts } from './components/graficos.js';
// CORREÇÃO: Nome do arquivo no plural e funções corretas
import { renderizarAnaliseComparativa, renderizarDetalhamento } from './components/tabelas.js';

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = await handleUpload(e.target);
    
    if (data && !data.error) {
        updateIndices(data.indices, data.dre);
        renderCharts(data.dre);
        renderizarAnaliseComparativa(data.tabela_patrimonial);
        
        const anos = Object.keys(data.anos || {}).sort();
        if (anos.length > 0) {
            renderizarDetalhamento(data.anos[anos[anos.length - 1]]);
        }
    } else if (data?.error) {
        alert(data.error);
    }
});