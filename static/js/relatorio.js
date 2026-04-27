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
    const [edu, sau, tri] = await Promise.all([
         buscarDados('educacao', 'total-educacao'),
         buscarDados('saude', 'total-saude'),
         buscarDados('tributario', 'total-tributario')
    ]);
/* ==============================
       BUSCA DADOS DINÂMICOS
============================== */
    const statusResp = await fetch('/api/status/geral');
    const status = await statusResp.json();
    const pizzaResp = await fetch('/api/pizza/saude');
    const pizza = await pizzaResp.json();
    const pizzaLabels = Object.keys(pizza);
    const pizzaValores = Object.values(pizza);
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
        options: {
            plugins: {
                legend: { display: false }
            }
        }
    });
    /* GRÁFICO 2 - STATUS */
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
                backgroundColor: ['#3498db', '#f39c12', '#2ecc71']
            }]
        }
    });
              /* GRÁFICO 3 - PIZZA */
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