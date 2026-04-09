// 1. Função para Chamar a Próxima Senha (Seguindo o padrão da Educação)
async function chamarSenha(setor) {
    try {
        // Usando a mesma rota que funcionou na educação
        const response = await fetch(`/api/chamar_proximo/${setor}`);
        const data = await response.json();

        if (data.erro) {
            alert("Não há pessoas aguardando no setor de Tributação.");
        } else {
            // Mapeando os IDs do seu HTML do Tributário
            document.getElementById('senha-atual').innerText = data.codigo;
            document.getElementById('tipo-atual').innerText = data.tipo;

            // Alerta sonoro
            const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play().catch(e => console.log("Som bloqueado pelo navegador"));

            atualizarStatus(); // Atualiza os números após chamar
        }
    } catch (error) {
        console.error("Erro ao processar chamada no tributário:", error);
    }
}

// 2. Função para atualizar os cards (Com os IDs específicos do Tributário)
async function atualizarStatus() {
    try {
        // Se a Educação usa /api/dashboard, usaremos aqui também para manter o padrão
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        if (data && !data.erro) {
            // No seu HTML do Tributário, os IDs começam com "count-"
            document.getElementById('count-aguardando').innerText = data.aguardando || 0;
            document.getElementById('count-atendimento').innerText = data.atendimento || 0;
            document.getElementById('count-finalizados').innerText = data.finalizado || 0;
        }
    } catch (e) {
        console.error("Erro ao buscar dados do dashboard tributário");
    }
}

// 3. Inicialização e Polling
setInterval(atualizarStatus, 5000); // Atualiza a cada 5 segundos
window.onload = atualizarStatus;