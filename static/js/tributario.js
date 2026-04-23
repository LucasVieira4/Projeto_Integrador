// 1. Função para Chamar a Próxima Senha (Seguindo o padrão da Educação)
async function chamarSenha(servico) {
    try {
        // Usando a mesma rota que funcionou na educação
        const response = await fetch(`/api/chamar_proximo/tributario/${servico}`);
        const data = await response.json();

        if (data.erro) {
            alert("Não há pessoas aguardando.");
            return;
        }
         const campo = document.getElementById(`ultima-${servico}`);
         if (campo){
             campo.innerText = data.codigo;
         }
            // Alerta sonoro
         const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
         audio.play().catch(e => console.log("Som bloqueado pelo navegador"));

         atualizarStatus(); // Atualiza os números após chamar

    } catch (error) {
        console.error("Erro:", error);
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

            document.getElementById('atend-iptu').innerText = data.aguardando_iptu || 0;
            document.getElementById('atend-iss').innerText = data.aguardando_iss || 0;
            document.getElementById('atend-alvara').innerText = data.aguardando_alvara || 0;
            document.getElementById('atend-divida').innerText = data.aguardando_divida || 0;
            document.getElementById('atend-certidoes').innerText = data.aguardando_certidoes || 0;
            document.getElementById('atend-cadastro').innerText = data.aguardando_cadastro || 0;
        }
    } catch (e) {
        console.error("Erro ao buscar dados do dashboard tributário");
    }
}

// 3. Inicialização e Polling
setInterval(atualizarStatus, 5000); // Atualiza a cada 5 segundos
window.onload = atualizarStatus;