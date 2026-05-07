async function buscarDados(setor, elementoId) {

    try {

        const response = await fetch(`/api/relatorio/${setor}`);
        const dados = await response.json();

        const total = dados.total_atendimentos || 0;

        document.getElementById(elementoId).innerText = total;

        return total;

    } catch (error) {

        console.error("Erro:", error);
        return 0;
    }
}

async function inicializarDashboard() {

    // ==============================
    // TOTAL SETOR
    // ==============================

    const total = await buscarDados(
        setor,
        `total-${setor}`
    );

    // ==============================
    // STATUS
    // ==============================

    const statusResp = await fetch('/api/status');
    const status = await statusResp.json();

    // ==============================
    // PIZZA
    // ==============================

    const pizzaResp = await fetch(`/api/pizza/${setor}`);
    const pizza = await pizzaResp.json();

    const pizzaLabels = Object.keys(pizza);
    const pizzaValores = Object.values(pizza);

    // ==============================
    // DIÁRIO
    // ==============================

    const diarioResp = await fetch(`/api/diario/${setor}`);
    const diario = await diarioResp.json();

    // ==============================
    // GRÁFICO SETOR
    // ==============================

    new Chart(document.getElementById('graficoSetor'), {

        type: 'bar',

        data: {

            labels: [setor.toUpperCase()],

            datasets: [{
                data: [total],
                backgroundColor: ['#3498db']
            }]
        },

        options: {
            plugins: {
                legend: { display: false }
            }
        }
    });

    // ==============================
    // STATUS
    // ==============================

    new Chart(document.getElementById('graficoStatus'), {

        type: 'bar',

        data: {

            labels: ['Aguardando', 'Em atendimento', 'Finalizado'],

            datasets: [{

                data: [
                    status.aguardando || 0,
                    status.atendimento || 0,
                    status.finalizado || 0
                ],

                backgroundColor: [
                    '#3498db',
                    '#f39c12',
                    '#2ecc71'
                ]
            }]
        }
    });

    // ==============================
    // PIZZA
    // ==============================

    new Chart(document.getElementById('graficoPizza'), {

        type: 'pie',

        data: {

            labels: pizzaLabels,

            datasets: [{

                data: pizzaValores,

                backgroundColor: [
                    '#3498db',
                    '#f39c12',
                    '#2ecc71',
                    '#9b59b6',
                    '#e74c3c',
                    '#1abc9c'
                ]
            }]
        }
    });

    // ==============================
    // LINHA
    // ==============================

    new Chart(document.getElementById('graficoLinha'), {

        type: 'line',

        data: {

            labels: diario.labels,

            datasets: [{

                label: 'Atendimentos',

                data: diario.valores,

                borderColor: '#3498db',

                fill: false
            }]
        }
    });
}

inicializarDashboard();