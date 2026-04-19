// CHAMAR SENHA POR SERVIÇO
async function chamarSenha(servico) {
    try {
        const response = await fetch(`/api/chamar_proximo/educacao/${servico}`);
        const data = await response.json();

        if (data.erro) {
            alert("Não há pessoas aguardando para " + servico);
        } else {

            // atualiza última senha chamada
            const idUltima = servico === "geral"
                ? "ultima-geral"
                : "ultima-" + servico;

            document.getElementById(idUltima).innerText = data.codigo;

            // som
            const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
            audio.play().catch(e => console.log("Som bloqueado"));

            atualizarMiniDashboard();
        }

    } catch (error) {
        console.error("Erro ao chamar senha:", error);
    }
}


// ATUALIZA DASHBOARD
async function atualizarMiniDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        if (data.erro) return;

        // cards superiores
        document.getElementById('aguardando').innerText = data.aguardando || 0;
        document.getElementById('atendimento').innerText = data.atendimento || 0;
        document.getElementById('finalizados').innerText = data.finalizado || 0;

        // filas aguardando
        document.getElementById('fila-matriculas').innerText = data.aguardando_matriculas || 0;
        document.getElementById('fila-documentos').innerText = data.aguardando_documentos || 0;
        document.getElementById('fila-transporte').innerText = data.aguardando_transporte || 0;
        document.getElementById('fila-creches').innerText = data.aguardando_creches || 0;
        document.getElementById('fila-inclusao').innerText = data.aguardando_inclusao || 0;
        document.getElementById('fila-geral').innerText = data.aguardando_geral || 0;

        // em atendimento
        document.getElementById('atend-matriculas').innerText = data.atend_matriculas || 0;
        document.getElementById('atend-documentos').innerText = data.atend_documentos || 0;
        document.getElementById('atend-transporte').innerText = data.atend_transporte || 0;
        document.getElementById('atend-creches').innerText = data.atend_creches || 0;
        document.getElementById('atend-inclusao').innerText = data.atend_inclusao || 0;
        document.getElementById('atend-geral').innerText = data.atend_geral || 0;

    } catch (error) {
        console.error("Erro ao atualizar painel");
    }
}


// AUTO UPDATE
setInterval(atualizarMiniDashboard, 5000);
window.onload = atualizarMiniDashboard;