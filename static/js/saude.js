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
            // Abre o modal de cadastro automaticamente
            abrirModal(data.codigo);
            atualizarMiniDashboard();

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


        // Função abrir fechar modal
        function abrirModal(codigo) {
            document.getElementById('modal-senha-titulo').innerText = codigo;
            document.getElementById('modalCadastro').style.display = 'block';
        }
        function fecharModal() {
            document.getElementById('modalCadastro').style.display = 'none';
            document.getElementById('formCadastro').reset();
        }
        //manipular o envio do formulário
        document.getElementById('formCadastro').onsubmit = async (e) => {e.preventDefault();

        const dados = {
            codigo: document.getElementById('modal-senha-titulo').innerText,
            nome: document.getElementById('cad-nome').value,
            nascimento: document.getElementById('cad-nascimento').value,
            filiacao: document.getElementById('cad-filiacao').value,
            endereco: document.getElementById('cad-endereco').value,
            especialidade: document.getElementById('cad-especialidade').value
        };
        const response = await fetch('/api/cadastrar_atendimento', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dados)
            });

            if (response.ok) {
                alert("Paciente encaminhado com sucesso!");
                fecharModal();
                atualizarMiniDashboard();
            }
        };

        // 2. Função para atualizar os cards (Azul, Laranja, Verde)
        async function atualizarMiniDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();

                if (data && !data.erro) {

                    const especialidades = [
                        { id: 'clinico', count: data.contagem_clinico },
                        { id: 'pediatria', count: data.contagem_pediatria },
                        { id: 'ortopedia', count: data.contagem_ortopedia },
                        { id: 'odontologia', count: data.contagem_odontologia },
                        { id: 'vacina', count: data.contagem_vacinas } // ✅ corrigido
                    ];

                    especialidades.forEach(esp => {
                        const card = document.getElementById(`card-${esp.id}`);
                        const span = document.getElementById(`atend-${esp.id}`);

                        // Atualiza número
                        if (span) {
                            span.innerText = esp.count || 0;
                        }

                        // ✅ SEM ESCONDER OS CARDS
                        if (card) {
                            card.style.display = 'block';
                        }
                    });
                }
            } catch (e) {
                console.log("Erro na atualização", e);
            }
        }

        // 3. Configurações Iniciais
        // Atualiza os contadores a cada 5 segundos automaticamente
        setInterval(atualizarMiniDashboard, 5000);

        // Busca dados assim que a página abre
        window.onload = atualizarMiniDashboard;