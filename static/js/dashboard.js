function processarDadosParaDashboard(data) {
    const fileNames = Object.keys(data);
    
    // 1. Localizar arquivos específicos no objeto
    const balanceteKey = fileNames.find(n => n.toLowerCase().includes('balancete'));
    const dreKey = fileNames.find(n => n.toLowerCase().includes('dre'));

    let resumo = { ativo: 0, passivo: 0, receita: 0, lucro: 0 };

    // 2. Cálculos do Balancete
    if (balanceteKey) {
        const contas = data[balanceteKey].contas;
        // Busca direta na raiz da árvore
        resumo.ativo = contas.find(c => c.descricao === "ATIVO")?.valores.saldo_atual || 0;
        resumo.passivo = contas.find(c => c.descricao === "PASSIVO")?.valores.saldo_atual || 0;
    }

    // 3. Cálculos da DRE
    if (dreKey) {
        const contasDre = data[dreKey].contas;
        // Busca recursiva ou direta dependendo da profundidade
        resumo.receita = contasDre.find(c => c.descricao.includes("RECEITA BRUTA"))?.valor || 0;
        resumo.lucro = contasDre.find(c => c.descricao.includes("PREJUÍZO") || c.descricao.includes("LUCRO"))?.valor || 0;
        
        atualizarGraficoReceitas(contasDre);
    }

    // 4. Preenchimento do HTML (Cards do seu projeto Emerald)
    atualizarUI(resumo, data[fileNames[0]].metadata);
}

function atualizarUI(resumo, meta) {
    document.getElementById('nome-empresa').innerText = meta.empresa;
    document.getElementById('cnpj-empresa').innerText = meta.cnpj;

    // IDs baseados no seu dashboard.html
    document.getElementById('valor-ativo').innerText = formatarMoeda(resumo.ativo);
    document.getElementById('valor-passivo').innerText = formatarMoeda(resumo.passivo);
    document.getElementById('valor-receita').innerText = formatarMoeda(resumo.receita);
    document.getElementById('valor-resultado').innerText = formatarMoeda(resumo.lucro);
    
    // Lógica visual: Vermelho se prejuízo, verde se lucro
    const elResultado = document.getElementById('valor-resultado');
    elResultado.style.color = resumo.lucro < 0 ? '#ef4444' : '#10b981';
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}