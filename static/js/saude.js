async function chamarSenha(setor) {
            try {
                const response = await fetch(`/api/chamar_proximo/${setor}`);
                const data = await response.json();

                if (data.erro) {
                    alert("Não há pacientes aguardando no setor de Saúde.");
                } else {
                    // Atualiza o visor central com a nova senha
                    document.getElementById('senha-atual').innerText = data.codigo;
                    document.getElementById('tipo-atual').innerText = data.tipo;

                    // Alerta sonoro opcional
                    const audio = new Audio('https://www.soundjay.com/buttons/beep-01a.mp3');
                    audio.play().catch(e => console.log("Áudio bloqueado pelo navegador"));

                    // Atualiza os contadores imediatamente
                    atualizarMiniDashboard();
                }
            } catch (error) {
                console.error("Erro ao processar chamada:", error);
            }
        }

        // 2. Função para atualizar os cards (Azul, Laranja, Verde)
        async function atualizarMiniDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();

                // Verificamos se o Python retornou os dados e se os IDs existem na tela
                if (data && !data.erro) {
                    document.getElementById('count-aguardando').innerText = data.aguardando || 0;
                    document.getElementById('count-atendimento').innerText = data.atendimento || 0;
                    // Note que no Python usamos 'finalizado', aqui garantimos a sincronia
                    document.getElementById('count-finalizados').innerText = data.finalizado || 0;
                }
            } catch (e) {
                console.log("Erro ao buscar dados do dashboard");
            }
        }

        // 3. Configurações Iniciais
        // Atualiza os contadores a cada 5 segundos automaticamente
        setInterval(atualizarMiniDashboard, 5000);

        // Busca dados assim que a página abre
        window.onload = atualizarMiniDashboard;