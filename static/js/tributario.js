async function chamarProximo() {
    // Como o arquivo é tributario.js, definimos o setor direto aqui
    const setorAtual = 'tributario';

    try {
        const response = await fetch(`/api/chamar_proximo/${setorAtual}`);
        const data = await response.json();

        if (data.erro) {
            alert("Fila vazia para o setor Tributário.");
            document.getElementById('senha-atual').innerText = "---";
            document.getElementById('tipo-atual').innerText = "Nenhum";
        } else {
            // Atualiza o visor central
            document.getElementById('senha-atual').innerText = data.codigo;
            document.getElementById('tipo-atual').innerText = data.tipo;

            // Som de alerta
            const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();

            // Atualiza os cards de números imediatamente após chamar
            atualizarMiniDashboard();
        }
    } catch (error) {
        console.error("Erro ao chamar senha:", error);
    }
}

async function atualizarMiniDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        // ATENÇÃO: Verifique se no seu HTML o ID é 'count-aguardando' ou 'card-aguardando'
        // No HTML que montamos antes, usamos 'count-...'
        if(document.getElementById('count-aguardando')) {
            document.getElementById('count-aguardando').innerText = data.aguardando;
            document.getElementById('count-atendimento').innerText = data.atendimento;
            document.getElementById('count-finalizados').innerText = data.finalizados;
        }
    } catch (e) {
        console.log("Erro ao atualizar dashboard");
    }
}

// Atualiza os números a cada 10 segundos
setInterval(atualizarMiniDashboard, 10000);

// Executa assim que a página abre
window.onload = atualizarMiniDashboard;