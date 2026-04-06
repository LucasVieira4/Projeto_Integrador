async function buscarDados(setor, elementoId) {
    try {
        const response = await fetch(`/api/relatorio/${setor}`);
        const dados = await response.json();
        document.getElementById(elementoId).innerText = dados.total_atendimentos;
        return dados.total_atendimentos;
    } catch (error) {
        console.error("Erro:", error);
        return 0;
    }
}

async function inicializarDashboard() {

    const [edu, sau, tri] = await Promise.all([
        buscarDados('educacao', 'total-educacao'),
        buscarDados('saude', 'total-saude'),
        buscarDados('tributario', 'total-tributario')
    ]);

    /* GRÁFICO 1 - BARRAS (SETOR) */
    new Chart(document.getElementById('graficoSetor'), {
        type: 'bar',
        data: {
            labels: ['Educação', 'Saúde', 'Tributário'],
            datasets: [{
                data: [edu, sau, tri],
                backgroundColor: ['#3498db', '#e74c3c', '#2ecc71']
            }]
        },
        options: { plugins: { legend: { display: false } } }
    });

    /* GRÁFICO 2 - STATUS */
    new Chart(document.getElementById('graficoStatus'), {
        type: 'bar',
        data: {
            labels: ['Aguardando', 'Em atendimento', 'Finalizado'],
            datasets: [{
                data: [10, 5, 21],
                backgroundColor: ['#3498db', '#f39c12', '#2ecc71']
            }]
        }
    });

    /* GRÁFICO 3 - PIZZA */
    new Chart(document.getElementById('graficoPizza'), {
        type: 'pie',
        data: {
            labels: ['Clínico Geral', 'Pediatria', 'Ortopedia'],
            datasets: [{
                data: [45, 35, 20],
                backgroundColor: ['#3498db', '#f39c12', '#2ecc71']
            }]
        }
    });

    /* GRÁFICO 4 - LINHA */
    new Chart(document.getElementById('graficoLinha'), {
        type: 'line',
        data: {
            labels: ['01/04', '05/04', '10/04', '15/04', '20/04', '25/04'],
            datasets: [{
                label: 'Atendimentos',
                data: [12, 15, 14, 18, 22, 20],
                borderColor: '#3498db',
                fill: false
            }]
        }
    });
}

inicializarDashboard();