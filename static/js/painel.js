let ultimaSenhaChamada = "";

async function atualizarPainelCompleto() {
    try {
        const response = await fetch('/api/painel_completo');
        if (!response.ok) throw new Error("Erro na requisição");
        const data = await response.json();

        // --- 1. SENHA ATUAL (CHAMADA PRINCIPAL) ---
        if (data.atual) {
            const senhaPrincipal = document.getElementById('senha-principal');
            if (senhaPrincipal && data.atual.codigo !== ultimaSenhaChamada) {
                senhaPrincipal.innerText = data.atual.codigo;
                document.getElementById('setor-principal').innerText = data.atual.setor.toUpperCase();
                document.getElementById('tipo-principal').innerText = data.atual.tipo;

                // Toca o som
                const audio = document.getElementById('audio-chamada');
                if (audio) audio.play().catch(e => console.log("Som bloqueado pelo navegador"));

                // Efeito visual de alerta
                document.body.classList.add('alerta-chamada');
                setTimeout(() => { document.body.classList.remove('alerta-chamada'); }, 2000);

                ultimaSenhaChamada = data.atual.codigo;
            }
        }

        // --- 2. PRÓXIMOS NA FILA ---
        const divProximos = document.getElementById('lista-proximos');
        if (divProximos && data.proximos) {
            divProximos.innerHTML = data.proximos.map(s =>
                `<div class="item-proximo">
                    <strong>${s.codigo}</strong>
                    <small>${s.setor.toUpperCase()}</small>
                </div>`
            ).join('');
        }

        // --- 3. ÚLTIMAS CHAMADAS (HISTÓRICO) ---
        const listaHistorico = document.getElementById('lista-historico');
        if (listaHistorico && data.finalizados) {
            // O .innerHTML limpa a lista antiga e o .map coloca na ordem do Python
            listaHistorico.innerHTML = data.finalizados.map(s => `
                <div class="item-historico">
                    <span>${s.codigo}</span>
                    <small>${s.setor.toUpperCase()}</small>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error("Erro ao atualizar painel:", error);
    }
}

// Inicia o loop
setInterval(atualizarPainelCompleto, 3000);
window.onload = atualizarPainelCompleto;