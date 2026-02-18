export async function handleUpload(formElement) {
    const formData = new FormData();
    // CORREÇÃO: Use o ID ou o Name exato do seu input no HTML
    const fileInput = document.getElementById('pdf-input') || formElement.querySelector('input[type="file"]');
    
    if (!fileInput || !fileInput.files.length) {
        alert("Por favor, selecione os arquivos.");
        return null;
    }

    for (const file of fileInput.files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/processar', {
            method: 'POST',
            body: formData
        });

        if (response.status === 400) throw new Error("Erro 400: Verifique o nome do campo de upload.");
        if (!response.ok) throw new Error("Erro no servidor (500). Verifique o terminal.");

        return await response.json();
    } catch (err) {
        console.error(err);
        return null;
    }
}