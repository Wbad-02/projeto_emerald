/**
 * Teste de Unidade: Validação de Lógica de Índices no Terminal
 * Para rodar: node teste_indices_terminal.js
 */

const IndicesLogic = {
    getLiquidezStatus: (v) => v > 2 ? 'Excelente' : v >= 1.5 ? 'Bom' : v >= 1.0 ? 'Atenção' : 'Crítico',
    getEndividamentoStatus: (v) => v < 30 ? 'Excelente' : v <= 50 ? 'Bom' : v <= 70 ? 'Atenção' : 'Crítico'
};

const scenarios = [
    { name: "Liquidez Excelente", val: 2.5, type: 'liq', expected: 'Excelente' },
    { name: "Liquidez Crítica", val: 0.8, type: 'liq', expected: 'Crítico' },
    { name: "Endividamento Bom", val: 45, type: 'endiv', expected: 'Bom' },
    { name: "Endividamento Crítico", val: 85, type: 'endiv', expected: 'Crítico' }
];

console.log("\x1b[36m%s\x1b[0m", "=== TESTE DE LOGICA DE INDICES (TERMINAL) ===");

scenarios.forEach(s => {
    const result = s.type === 'liq' ? IndicesLogic.getLiquidezStatus(s.val) : IndicesLogic.getEndividamentoStatus(s.val);
    const pass = result === s.expected;
    const color = pass ? "\x1b[32m" : "\x1b[31m";
    console.log(`${s.name}: [${s.val}] -> Result: ${color}${result}\x1b[0m | Pass: ${pass ? '✅' : '❌'}`);
});