// 1. Função para Chamar a Próxima Senha (Igual ao Saúde)
async function chamarSenha(setor) {
    try {
        const response = await fetch(`/api/chamar_proximo/${setor}`);
        const data = await response.json();

        if (data.erro) {
            alert("Não há pessoas aguardando no setor de Educação.");
        } else {
            // ATENÇÃO: Verifique se esses IDs existem no seu HTML de Educação
            document.getElementById('senha-atual').innerText = data.codigo;
            document.getElementById('tipo-atual').innerText = data.tipo;

            const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play().catch(e => console.log("Som bloqueado"));

            atualizarMiniDashboard(); // Atualiza os números após chamar
        }
    } catch (error) {
        console.error("Erro ao processar chamada:", error);
    }
}

// 2. Função para atualizar os cards (Adaptada para os IDs do seu HTML de Educação)
async function atualizarMiniDashboard() {
    try {
        // Usamos a rota geral /api/dashboard que já verifica o setor na sessão (Python)
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        if (data && !data.erro) {
            // AQUI ESTÁ O PULO DO GATO:
            // No seu HTML de Educação, os IDs são 'aguardando', 'atendimento', 'finalizados'
            // Sem o prefixo "count-" que você usou na Saúde.
            document.getElementById('aguardando').innerText = data.aguardando || 0;
            document.getElementById('atendimento').innerText = data.atendimento || 0;
            document.getElementById('finalizados').innerText = data.finalizado || 0;
        }
    } catch (e) {
        console.log("Erro ao buscar dados do dashboard");
    }
}

// 3. Inicialização
setInterval(atualizarMiniDashboard, 5000);
window.onload = atualizarMiniDashboard;
