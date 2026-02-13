document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    if(!form) return;

    const input = document.getElementById('file-input');
    const list = document.getElementById('file-list');

    input.addEventListener('change', (e) => {
        list.innerHTML = '';
        Array.from(e.target.files).forEach(f => list.innerHTML += `<div>📄 ${f.name}</div>`);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if(input.files.length === 0) return alert('Selecione arquivos');
        
        const btn = form.querySelector('button');
        btn.innerText = 'Processando...';
        btn.disabled = true;

        const fd = new FormData();
        for(let f of input.files) fd.append('pdf-input', f);

        try {
            const res = await fetch('/processar', {method:'POST', body:fd});
            const data = await res.json();
            
            if(data.error) throw new Error(data.error);
            
            // Dispara evento global
            window.dispatchEvent(new CustomEvent('dados-prontos', {detail: data}));
            
        } catch(err) {
            alert(err.message);
        } finally {
            btn.innerText = '🚀 Processar';
            btn.disabled = false;
        }
    });
});