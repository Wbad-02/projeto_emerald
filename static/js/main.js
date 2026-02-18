import { IndicesComponent } from './components/indices.js';
import { TabelasComponent } from './components/tabelas.js';
import { GraficosComponent } from './components/graficos.js';
import { RegimesComponent } from './components/regimes.js'; 

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const btnProcessar = document.getElementById('btn-processar');
    const loader = document.getElementById('loader');
    const dashboardContent = document.getElementById('dashboard-content');

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const files = fileInput.files;
            if (files.length === 0) {
                alert("Por favor, selecione os arquivos da Itasul (Balancete e DRE).");
                return;
            }

            setLoadingState(true);
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            try {
                const response = await fetch('/processar', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                if (response.ok) {
                    renderizarDashboard(result);
                } else {
                    alert("Erro no servidor: " + result.error);
                }
            } catch (error) {
                console.error("Erro na comunicação com a API:", error);
                alert("Não foi possível conectar ao servidor.");
            } finally {
                setLoadingState(false);
            }
        });
    }

    function renderizarDashboard(dados) {
        console.log("Emerald Data:", dados);
        const p = dados.indices;

        [cite_start]// 1. Informações do Cabeçalho (Metadados da Empresa) [cite: 84, 85, 86]
        const elRazao = document.getElementById('info-razao');
        if (elRazao) elRazao.innerText = dados.empresa || "ITASUL TRANSPORTE E LOGISTICA LTDA";
        
        const elCnpj = document.getElementById('info-cnpj');
        if (elCnpj && dados.cnpj) elCnpj.innerText = dados.cnpj;

        const elPeriodo = document.getElementById('info-periodo');
        if (elPeriodo && dados.periodo) elPeriodo.innerText = dados.periodo;
        
        // 2. Renderização dos Componentes Visuais
        IndicesComponent.render(dados);
        TabelasComponent.render(dados);
        GraficosComponent.render(dados);
        RegimesComponent.render(dados); 

        // 3. Geração de Insights e Configuração do Especialista
        preencherInsights(p);
        
        // Proteção contra erro de nulo se o elemento ainda não existir no DOM
        if (document.getElementById('btn-salvar-recomendacao')) {
            configurarRecomendacaoEspecialista();
        }
        
        // 4. Exibição do Dashboard
        if (dashboardContent) {
            dashboardContent.classList.remove('hidden');
            dashboardContent.scrollIntoView({ behavior: 'smooth' });
        }
    }

    function configurarRecomendacaoEspecialista() {
        const btn = document.getElementById('btn-salvar-recomendacao');
        const input = document.getElementById('texto-especialista');
        const listaRecomendacoes = document.getElementById('recomendacoes-lista');

        if (!btn || !input || !listaRecomendacoes) return;

        // Previne a criação de múltiplos listeners clonando o botão
        const novoBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(novoBtn, btn);

        novoBtn.addEventListener('click', () => {
            const texto = input.value.trim();
            if (texto === "") return;

            [cite_start]// Cria o elemento com a formatação "Recomendação Especialista Upgrade" [cite: 137]
            const div = document.createElement('div');
            div.className = "border-l-4 border-emerald-400 pl-4 bg-slate-800 p-4 rounded-r-xl mb-4 animate-fade-in";
            div.innerHTML = `
                <p class="font-black text-[10px] text-emerald-400 uppercase tracking-widest mb-2">Recomendação Especialista Upgrade</p>
                <p class="text-sm text-slate-200 leading-relaxed font-medium italic">"${texto}"</p>
            `;

            listaRecomendacoes.prepend(div);
            input.value = "";
        });
    }

    function preencherInsights(p) {
        const positivos = document.getElementById('pontos-positivos');
        const negativos = document.getElementById('pontos-negativos');
        const recomendacoes = document.getElementById('recomendacoes-lista');

        if (!positivos || !negativos || !recomendacoes) return;

        positivos.innerHTML = '';
        negativos.innerHTML = '';
        recomendacoes.innerHTML = '';

        [cite_start]// Lógica de Pontos Positivos baseada na ITASUL [cite: 88, 127]
        if (p.LUCRO_LIQ_PERC > 10) {
            positivos.innerHTML += `<li>✅ Margem líquida saudável de ${p.LUCRO_LIQ_PERC.toFixed(1)}%</li>`;
        }
        if (p.EBITDA > 0) {
            positivos.innerHTML += `<li>✅ EBITDA positivo apresentando crescimento operacional</li>`;
        }

        [cite_start]// Áreas de Atenção (Endividamento Crítico) [cite: 88, 129]
        if (p.endiv_geral > 50) {
            negativos.innerHTML += `<li>⚠️ Endividamento Geral elevado em ${p.endiv_geral.toFixed(1)}% demanda atenção</li>`;
        }
        if (p.liq_corrente < 1.0) {
            negativos.innerHTML += `<li>⚠️ Liquidez corrente de ${p.liq_corrente.toFixed(2)} indica risco de solvência a curto prazo</li>`;
        }

        [cite_start]// Recomendações Prioritárias (Limpas sem [cite]) [cite: 130, 131, 133, 135]
        recomendacoes.innerHTML = `
            <div class="border-l-4 border-emerald-500 pl-4">
                <p class="font-bold text-sm">Gestão Conservadora</p>
                <p class="text-xs opacity-80">Manter planejamento de investimentos estratégicos.</p>
            </div>
            <div class="border-l-4 border-yellow-500 pl-4">
                <p class="font-bold text-sm">Otimização Tributária</p>
                <p class="text-xs opacity-80">Avaliar transição entre regimes para reduzir carga fiscal.</p>
            </div>
            <div class="border-l-4 border-blue-500 pl-4">
                <p class="font-bold text-sm">Monitoramento de KPIs</p>
                <p class="text-xs opacity-80">Implementar sistema de indicadores contínuos.</p>
            </div>
        `;
    }

    function setLoadingState(isLoading) {
        if (loader) loader.classList.toggle('hidden', !isLoading);
        if (btnProcessar) {
            btnProcessar.disabled = isLoading;
            btnProcessar.innerText = isLoading ? "Analisando..." : "Analisar Documentos";
        }
    }
});