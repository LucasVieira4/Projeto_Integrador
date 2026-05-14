async function inicializarDashboard() {

    try {

        // ==============================
        // STATUS
        // ==============================

        const statusResp = await fetch('/api/status');
        const status = await statusResp.json();

        // ==============================
        // CARDS SUPERIORES
        // ==============================

        document.getElementById('card-aguardando').innerText =
            status.aguardando || 0;

        document.getElementById('card-atendimento').innerText =
            status.atendimento || 0;

        document.getElementById('card-finalizado').innerText =
            status.finalizado || 0;

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
        // GRÁFICO RESUMO
        // ==============================

        new Chart(document.getElementById('graficoSetor'), {

            type: 'bar',

            data: {

                labels: [
                    'Aguardando',
                    'Em atendimento',
                    'Finalizado'
                ],

                datasets: [{

                    label: 'Atendimentos',

                    data: [
                        status.aguardando || 0,
                        status.atendimento || 0,
                        status.finalizado || 0
                    ],

                    backgroundColor: [
                        '#f39c12',
                        '#3498db',
                        '#2ecc71'
                    ]
                }]
            },

            options: {

                responsive: true,

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // ==============================
        // STATUS
        // ==============================

        new Chart(document.getElementById('graficoStatus'), {

            type: 'bar',

            data: {

                labels: [
                    'Aguardando',
                    'Em atendimento',
                    'Finalizado'
                ],

                datasets: [{

                    label: 'Atendimentos',

                    data: [
                        status.aguardando || 0,
                        status.atendimento || 0,
                        status.finalizado || 0
                    ],

                    backgroundColor: [
                        '#f39c12',
                        '#3498db',
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

    } catch (error) {

        console.error("Erro ao carregar dashboard:", error);
    }
}

inicializarDashboard();