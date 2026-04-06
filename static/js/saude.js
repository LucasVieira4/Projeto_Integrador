async function chamarProximo() {
    // Definimos o setor manualmente para este arquivo específico
    const setorAtual = 'saude';

    try {
        const response = await fetch(`http://192.168.15.4:5000/api/chamar_proximo/${setorAtual}`);
        const data = await response.json();

        if (data.erro) {
            alert("Fila vazia para o setor Saúde.");
            document.getElementById('senha-atual').innerText = "---";
            document.getElementById('tipo-atual').innerText = "Nenhum";
        } else {
            // Atualiza o visor de senha no painel central
            document.getElementById('senha-atual').innerText = data.codigo;
            document.getElementById('tipo-atual').innerText = data.tipo;

            // Som de alerta (Beep)
            const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play();

            // Atualiza os cards de números imediatamente
            atualizarMiniDashboard();
        }
    } catch (error) {
        console.error("Erro ao chamar senha:", error);
    }
}

// Função para atualizar os cards de estatísticas (os azuis/laranjas/verdes no topo)
async function atualizarMiniDashboard() {
    try {
        const response = await fetch('http://192.168.15.4:5000/api/dashboard');
        const data = await response.json();

        // Verificando se os elementos com os IDs corretos existem na tela
        if(document.getElementById('count-aguardando')) {
            document.getElementById('count-aguardando').innerText = data.aguardando;
            document.getElementById('count-atendimento').innerText = data.atendimento;
            document.getElementById('count-finalizados').innerText = data.finalizados;
        }
    } catch (e) {
        console.log("Erro ao atualizar dashboard");
    }
}

// Atualiza os números automaticamente a cada 10 segundos
setInterval(atualizarMiniDashboard, 10000);

// Faz a primeira busca assim que a página é carregada
window.onload = atualizarMiniDashboard;