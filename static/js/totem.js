async function gerarSenha(prioridade) {
    const setor = 'saude';

    try {
        const response = await fetch('http://localhost:5000/api/gerar_senha', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ setor: setor, prioridade: prioridade })
        });

        const data = await response.json();

        if (data.erro) {
            alert(`ERRO AO GERAR: ${data.erro}`);
        } else {
            // O código deve ser data.codigo e o tipo data.tipo
            alert(`SENHA GERADA: ${data.codigo}\nTipo: ${data.tipo}`);
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
        alert("Erro de conexão com o servidor.");
    }
}
