let ultimaSenhaChamada = "";

async function atualizarPainelCompleto() {
    try {
        const response = await fetch('/api/painel_completo');
        const data = await response.json();

        // --- 1. ATUALIZA A SENHA ATUAL (PRINCIPAL) ---
        if (data.atual) {
            const senhaPrincipal = document.getElementById('senha-principal');

            // Se a senha mudou, toca o som e pisca
            if (data.atual.codigo !== ultimaSenhaChamada) {
                senhaPrincipal.innerText = data.atual.codigo;
                document.getElementById('setor-principal').innerText = data.atual.setor.toUpperCase();
                document.getElementById('tipo-principal').innerText = data.atual.tipo;

                document.getElementById('audio-chamada').play().catch(e => console.log("Aguardando interação para som"));

                document.body.style.backgroundColor = "#e74c3c";
                setTimeout(() => { document.body.style.backgroundColor = "#1c2b4a"; }, 1000);

                ultimaSenhaChamada = data.atual.codigo;
            }
        }

        // --- 2. ATUALIZA A LISTA DE PRÓXIMOS (Pode criar um div no HTML para isso) ---
        // Se você tiver um <div id="lista-proximos"> no HTML:
        const divProximos = document.getElementById('lista-proximos');
        if (divProximos) {
            divProximos.innerHTML = data.proximos.map(s =>
                `<div class="item-proximo">${s.codigo} - <small>${s.setor}</small></div>`
            ).join('');
        }

        // --- 3. ATUALIZA O HISTÓRICO (FINALIZADOS) ---
        const listaHistorico = document.getElementById('lista-historico');
        listaHistorico.innerHTML = data.finalizados.map(s => `
            <div class="item-historico">
                <span>${s.codigo}</span>
                <small>${s.setor.toUpperCase()}</small>
            </div>
        `).join('');

    } catch (error) {
        console.error("Erro ao atualizar painel:", error);
    }
}

// Executa a cada 3 segundos
setInterval(atualizarPainelCompleto, 3000);
window.onload = atualizarPainelCompleto;