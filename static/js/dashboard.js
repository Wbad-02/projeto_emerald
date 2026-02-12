/**
 * DASHBOARD FINANCEIRO EMERALD
 * Lógica Front-end Completa (Etapas 1 a 8)
 */

// Configuração Global de Cores (Tema Emerald)
const COLORS = {
    emerald: '#10b981',
    emeraldDark: '#064e3b',
    red: '#ef4444',
    blue: '#3b82f6',
    yellow: '#f59e0b',
    gray: '#9ca3af'
};

Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.color = '#4a634a';

document.addEventListener('DOMContentLoaded', () => {
    inicializarUpload();
});

// ===========================================
// 🚀 INICIALIZAÇÃO
// ===========================================
function inicializarUpload() {
    const form = document.getElementById('upload-form');
    const input = document.getElementById('pdf-input');
    const list = document.getElementById('file-list');

    // UX: Mostra arquivos selecionados
    input.addEventListener('change', (e) => {
        list.innerHTML = '';
        Array.from(e.target.files).forEach(f => {
            list.innerHTML += `<div style="margin-bottom:4px;">📄 <b>${f.name}</b> <small class="text-muted">(${(f.size/1024).toFixed(0)} KB)</small></div>`;
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = form.querySelector('button');
        
        if (input.files.length === 0) return alert("Por favor, selecione os arquivos CSV ou Excel.");

        btn.innerHTML = "⏳ Processando Inteligência...";
        btn.disabled = true;

        const formData = new FormData();
        for (let f of input.files) formData.append('pdf-input', f);

        try {
            const res = await fetch('/processar', { method: 'POST', body: formData });
            const data = await res.json();
            
            if (data.error) throw new Error(data.error);

            // Troca de tela
            document.getElementById('upload-section').style.display = 'none';
            document.getElementById('dashboard-content').style.display = 'block';
            
            // Inicia o Pipeline de Análise
            executarPipeline(data);

        } catch (err) {
            alert("Erro no processamento: " + err.message);
            btn.innerHTML = "❌ Tentar Novamente";
        } finally {
            if (!document.getElementById('dashboard-content').style.display === 'block') {
                btn.disabled = false;
            }
        }
    });
}

// ===========================================
// 🧠 PIPELINE DE INTELIGÊNCIA
// ===========================================
function executarPipeline(data) {
    // 1. Identificação Temporal (Ano Anterior vs Atual)
    const arquivos = Object.keys(data).sort(); 
    const arqAnt = arquivos.length > 1 ? data[arquivos[0]] : null;
    const arqAtual = data[arquivos[arquivos.length - 1]];

    // Preenche Cabeçalho
    if (arqAtual.metadata) {
        setText('nome-empresa', arqAtual.metadata.empresa || "Empresa Não Identificada");
        setText('cnpj-empresa', "CNPJ: " + (arqAtual.metadata.cnpj || "--"));
    }

    // ETAPA 1: Extração
    const v = extrairValores(arqAtual, arqAnt);

    // ETAPA 2: Variações
    const variacoes = calcularVariacoes(v);

    // ETAPA 3: Índices
    const indices = calcularIndices(v);

    // ETAPA 4: Renderizar Tabelas e KPIs Numéricos
    renderizarTabelas(v, variacoes);
    renderizarCardsIndices(indices);

    // ETAPA 5: Gráficos
    renderizarGraficos(v, indices);

    // ETAPA 6: Pontos Positivos e Atenção
    gerarDiagnosticoQualitativo(v, variacoes, indices);

    // ETAPA 7: Comparação Tributária
    gerarSimulacaoTributaria(v);

    // ETAPA 8: Recomendações
    gerarRecomendacoes(v, indices);
}

// ===========================================
// 📊 ETAPA 1: EXTRAÇÃO DE VALORES
// ===========================================
function extrairValores(atualData, antData) {
    const getVal = (data, termos, classif) => {
        if (!data) return 0;
        return buscarValorConta(data.contas, termos, classif);
    };

    const par = (t, c) => ({
        atual: getVal(atualData, t, c),
        ant: getVal(antData, t, c)
    });

    return {
        // Balanço
        ativoCirc: par(['ATIVO CIRCULANTE'], '1.1'),
        ativoNaoCirc: par(['ATIVO NÃO CIRCULANTE', 'REALIZÁVEL A LONGO PRAZO'], '1.2'),
        ativoTotal: par(['ATIVO', 'TOTAL DO ATIVO'], '1'),
        passivoCirc: par(['PASSIVO CIRCULANTE'], '2.1'),
        passivoNaoCirc: par(['PASSIVO NÃO CIRCULANTE', 'EXIGÍVEL A LONGO PRAZO'], '2.2'),
        pl: par(['PATRIMÔNIO LÍQUIDO', 'PATRIMONIO LIQUIDO'], '2.3'),
        passivoTotal: par(['PASSIVO', 'TOTAL DO PASSIVO'], '2'),
        
        // Específicos para Índices
        disponivel: par(['CAIXA', 'BANCOS', 'DISPONIVEL'], '1.1.01'),
        estoques: par(['ESTOQUES', 'MERCADORIAS'], '1.1.03'),

        // DRE
        receitaBruta: par(['RECEITA BRUTA', 'RECEITA OPERACIONAL BRUTA']),
        receitaLiq: par(['RECEITA LÍQUIDA', 'RECEITA LIQUIDA']),
        lucroBruto: par(['LUCRO BRUTO', 'RESULTADO BRUTO']),
        despesasOp: par(['DESPESAS OPERACIONAIS']),
        lucroLiq: par(['LUCRO LÍQUIDO', 'PREJUÍZO DO EXERCÍCIO', 'RESULTADO DO EXERCÍCIO'])
    };
}

// ===========================================
// 📈 ETAPA 2: CÁLCULO DE VARIAÇÕES
// ===========================================
function calcularVariacoes(v) {
    let res = {};
    for (let k in v) {
        const diff = v[k].atual - v[k].ant;
        const perc = v[k].ant !== 0 ? (diff / Math.abs(v[k].ant)) * 100 : 0;
        
        let status = '● Estável';
        let colorClass = 'text-muted'; // Cinza

        if (perc > 0.1) { status = '▲ Crescimento'; colorClass = 'text-success'; } // Verde
        if (perc < -0.1) { status = '▼ Queda'; colorClass = 'text-danger'; } // Vermelho

        // Inverte lógica para Passivos/Despesas (Crescimento é ruim)
        if (['passivoCirc', 'passivoTotal', 'despesasOp'].includes(k)) {
             if (perc > 0.1) colorClass = 'text-danger';
             if (perc < -0.1) colorClass = 'text-success';
        }

        res[k] = { diff, perc, status, colorClass };
    }
    return res;
}

// ===========================================
// 🧮 ETAPA 3: ÍNDICES FINANCEIROS
// ===========================================
function calcularIndices(v) {
    const safeDiv = (n, d) => d !== 0 ? n / d : 0;
    const a = (k) => v[k].atual;

    return {
        // Liquidez
        liqCorrente: safeDiv(a('ativoCirc'), a('passivoCirc')),
        liqSeca: safeDiv(a('ativoCirc') - a('estoques'), a('passivoCirc')),
        liqImediata: safeDiv(a('disponivel'), a('passivoCirc')),
        
        // Rentabilidade
        margemLiq: safeDiv(a('lucroLiq'), a('receitaLiq')) * 100,
        roe: safeDiv(a('lucroLiq'), a('pl')) * 100,
        roa: safeDiv(a('lucroLiq'), a('ativoTotal')) * 100,
        
        // Endividamento
        endividamento: safeDiv(a('passivoCirc') + a('passivoNaoCirc'), a('ativoTotal')) * 100
    };
}

// ===========================================
// 📋 ETAPA 4: TABELAS E CARDS (Interface)
// ===========================================
function renderizarTabelas(v, vari) {
    const tbody = document.getElementById('tabela-comparativa-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    const linhas = [
        { l: 'Receita Bruta', k: 'receitaBruta' },
        { l: 'Lucro Líquido', k: 'lucroLiq' },
        { l: 'Ativo Total', k: 'ativoTotal' },
        { l: 'Patrimônio Líquido', k: 'pl' }
    ];

    linhas.forEach(item => {
        const val = v[item.k];
        const vr = vari[item.k];
        tbody.innerHTML += `
            <tr>
                <td style="font-weight:600">${item.l}</td>
                <td class="text-right">${fmtMoeda(val.ant)}</td>
                <td class="text-right">${fmtMoeda(val.atual)}</td>
                <td class="${vr.colorClass} text-center" style="font-weight:500">
                    ${vr.status} (${vr.perc.toFixed(1)}%)
                </td>
            </tr>
        `;
    });

    // Atualiza KPIs do Topo
    setText('valor-receita', fmtMoeda(v.receitaBruta.atual));
    setText('valor-ativo', fmtMoeda(v.ativoTotal.atual));
    setText('valor-passivo', fmtMoeda(v.passivoTotal.atual));
    
    const elRes = document.getElementById('valor-resultado');
    elRes.innerText = fmtMoeda(v.lucroLiq.atual);
    elRes.style.color = v.lucroLiq.atual >= 0 ? COLORS.emerald : COLORS.red;
}

function renderizarCardsIndices(idx) {
    setText('ind-liquidez', idx.liqCorrente.toFixed(2));
    setText('ind-margem', idx.margemLiq.toFixed(1) + '%');
    // Adicionar outros IDs se existirem no HTML (ex: endividamento)
}

// ===========================================
// 📊 ETAPA 5: GERAÇÃO DOS GRÁFICOS
// ===========================================
let chartInstance = null;

function renderizarGraficos(v, idx) {
    const ctx = document.getElementById('chart-principal');
    if (!ctx) return;

    if (chartInstance) chartInstance.destroy();

    // Gráfico: Composição do Resultado
    // Se Lucro > 0: Mostra Lucro vs Despesas
    // Se Prejuízo: Mostra Receita vs Prejuízo
    const lucro = v.lucroLiq.atual;
    const receita = v.receitaLiq.atual;
    
    let labels, data, colors;

    if (lucro >= 0) {
        const custos = Math.max(0, receita - lucro);
        labels = ['Lucro Líquido', 'Custos e Despesas'];
        data = [lucro, custos];
        colors = [COLORS.emerald, COLORS.red];
    } else {
        labels = ['Receita Gerada', 'Prejuízo Absorvido'];
        data = [receita, Math.abs(lucro)];
        colors = [COLORS.blue, COLORS.red];
    }

    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Eficiência Operacional' }
            }
        }
    });
}

// ===========================================
// ✅ ETAPA 6: PONTOS POSITIVOS E ATENÇÃO
// ===========================================
function gerarDiagnosticoQualitativo(v, vari, idx) {
    const divPositivos = document.getElementById('pontos-positivos'); // Crie esse ID no HTML se não houver
    const divAtencao = document.getElementById('pontos-atencao');     // Crie esse ID no HTML se não houver
    
    // Se os elementos não existirem no HTML, tenta injetar em um container genérico ou ignora
    if (!divAtencao) return; 

    let htmlPos = '';
    let htmlAtt = '';

    // Lógica de Diagnóstico
    if (vari.receitaLiq.perc > 10) 
        htmlPos += criarItemPonto(`Receita cresceu ${vari.receitaLiq.perc.toFixed(1)}% no período.`, 'check');
    
    if (idx.margemLiq > 15) 
        htmlPos += criarItemPonto(`Margem Líquida excelente de ${idx.margemLiq.toFixed(1)}%.`, 'check');

    if (idx.liqCorrente > 1.2)
        htmlPos += criarItemPonto(`Boa liquidez (R$ ${idx.liqCorrente.toFixed(2)} para cada R$ 1 de dívida).`, 'check');

    if (idx.liqCorrente < 1) 
        htmlAtt += criarItemPonto(`Risco de Liquidez: A empresa não paga suas dívidas de curto prazo (Índice: ${idx.liqCorrente.toFixed(2)}).`, 'alert');

    if (v.lucroLiq.atual < 0)
        htmlAtt += criarItemPonto(`Empresa opera com Prejuízo de ${fmtMoeda(v.lucroLiq.atual)}.`, 'alert');

    if (idx.endividamento > 70)
        htmlAtt += criarItemPonto(`Alto nível de endividamento (${idx.endividamento.toFixed(1)}% do Ativo).`, 'alert');

    divPositivos.innerHTML = htmlPos || '<div class="text-muted italic">Sem destaques positivos expressivos.</div>';
    divAtencao.innerHTML = htmlAtt || '<div class="text-muted italic">Sem pontos críticos de atenção.</div>';
}

function criarItemPonto(texto, tipo) {
    const icon = tipo === 'check' ? '✅' : '⚠️';
    const classe = tipo === 'check' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800';
    return `
        <div class="point-item ${classe} p-3 rounded mb-2 border text-sm flex items-start gap-2">
            <span>${icon}</span>
            <span>${texto}</span>
        </div>
    `;
}

// ===========================================
// 💰 ETAPA 7: COMPARAÇÃO TRIBUTÁRIA
// ===========================================
function gerarSimulacaoTributaria(v) {
    const receitaAnual = v.receitaBruta.atual; // Assume que o DRE é anual
    const lucroRealAnual = v.lucroLiq.atual; // Lucro Contábil (Simplificação para Lucro Real)
    
    if (receitaAnual === 0) return;

    // 1. Simples Nacional (Estimativa Anexo III/IV - Média 10%)
    // Em produção, precisaria de uma tabela progressiva completa
    const impostoSimples = receitaAnual * 0.10;

    // 2. Lucro Presumido (Serviços)
    // PIS/COFINS (3.65%) + IRPJ/CSLL (Presunção 32% -> Alíquota combinada ~11.33%)
    // Total Aprox: 15% sobre Receita
    const impostoPresumido = receitaAnual * 0.15;

    // 3. Lucro Real
    // PIS/COFINS (9.25% sobre Receita - Não Cumulativo) 
    // IRPJ/CSLL (34% sobre Lucro Líquido Ajustado)
    let impostoReal = (receitaAnual * 0.0925);
    if (lucroRealAnual > 0) {
        impostoReal += (lucroRealAnual * 0.34);
    }

    // Renderiza
    setText('tax-simples', fmtMoeda(impostoSimples));
    setText('tax-presumido', fmtMoeda(impostoPresumido));
    setText('tax-real', fmtMoeda(impostoReal));

    // Define recomendação visual
    const menorImposto = Math.min(impostoSimples, impostoPresumido, impostoReal);
    highlightTaxCard('tax-simples', impostoSimples, menorImposto);
    highlightTaxCard('tax-presumido', impostoPresumido, menorImposto);
    highlightTaxCard('tax-real', impostoReal, menorImposto);
}

function highlightTaxCard(id, valor, menor) {
    const card = document.getElementById(id).parentElement;
    // Remove estilos anteriores
    card.classList.remove('ring-4', 'ring-emerald-400', 'bg-emerald-50');
    
    if (Math.abs(valor - menor) < 1.0) { // Margem de erro float
        card.classList.add('ring-2', 'ring-emerald-500', 'bg-emerald-50');
        // Adiciona badge se não tiver
        if (!card.querySelector('.badge-rec')) {
            const badge = document.createElement('div');
            badge.className = 'badge-rec bg-emerald-500 text-white text-xs font-bold px-2 py-1 rounded absolute top-0 right-0 m-2';
            badge.innerText = 'RECOMENDADO';
            card.style.position = 'relative';
            card.appendChild(badge);
        }
    }
}

// ===========================================
// 💡 ETAPA 8: RECOMENDAÇÕES
// ===========================================
function gerarRecomendacoes(v, idx) {
    const container = document.getElementById('recomendacoes-container'); // Crie esse ID no HTML
    if (!container) return;

    let recs = [];

    // Lógica de Negócio para Recomendações
    if (idx.liqCorrente < 1) {
        recs.push("🚨 <b>Crítico:</b> Sua liquidez está abaixo de 1. Renegocie prazos com fornecedores imediatamente para evitar insolvência.");
    }
    
    if (v.despesasOp.atual > (v.receitaLiq.atual * 0.8)) {
        const economia = v.despesasOp.atual * 0.10;
        recs.push(`💡 <b>Eficiência:</b> Suas despesas operacionais consomem mais de 80% da receita. Uma redução de 10% geraria uma economia de <b>${fmtMoeda(economia)}</b>.`);
    }

    if (idx.roe < 5 && idx.roe > 0) {
        recs.push("📉 <b>Retorno:</b> O retorno sobre o patrimônio (ROE) está baixo (< 5%). Avalie se o capital estaria melhor investido em aplicações financeiras do que na operação atual.");
    }

    if (v.estoques.atual > v.receitaBruta.atual * 0.5) {
        recs.push("📦 <b>Estoque:</b> Nível de estoque muito alto em relação à venda. Realize promoções para girar o estoque parado e liberar caixa.");
    }

    // Renderiza HTML
    container.innerHTML = recs.map(texto => `
        <div class="recommendation-item bg-white border-l-4 border-blue-500 p-4 shadow-sm rounded mb-3 text-sm text-gray-700">
            ${texto}
        </div>
    `).join('') || '<div class="text-muted p-4">Nenhuma recomendação crítica baseada nos dados atuais.</div>';
}


// ===========================================
// 🛠 UTILITÁRIOS GERAIS
// ===========================================
function buscarValorConta(lista, termos, classif) {
    if (!lista) return 0;
    for (let c of lista) {
        const desc = c.descricao ? c.descricao.toUpperCase() : '';
        const codigo = c.classificacao || '';
        
        // Match por Classificação (ex: "1.1") ou Nome
        if ((classif && codigo.startsWith(classif)) || (termos && termos.some(t => desc.includes(t)))) {
            // Pega o valor (suporta DRE e Balancete)
            if (c.valor !== undefined) return c.valor;
            if (c.valores && c.valores.saldo_atual !== undefined) return c.valores.saldo_atual;
        }
        
        // Recursão
        if (c.filhos) {
            const found = buscarValorConta(c.filhos, termos, classif);
            if (found !== 0) return found;
        }
    }
    return 0;
}

function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.innerText = val;
}

function fmtMoeda(val) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
}