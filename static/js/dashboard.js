document.addEventListener('DOMContentLoaded', () => {
    // Atualiza a data automaticamente para o dia de hoje
    const dataHighlight = document.querySelector('.date-highlight');
    const dataSub = document.querySelector('.date-sub');

    if (dataHighlight && dataSub) {
        const agora = new Date();
        dataHighlight.textContent = agora.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric' });
        dataSub.textContent = `de ${agora.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}`;
    }

    // Faz os pontos da galeria (carousel-dots) funcionarem visualmente
    const dots = document.querySelectorAll('.dot');
    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            document.querySelector('.dot.active').classList.remove('active');
            dot.classList.add('active');
        });
    });
    // ====COTACAO DOLAR==============
     async function atualizarDolar() {

        try {

            const response = await fetch('/api/dolar');
            const dados = await response.json();

            document.getElementById('cotacao-dolar').innerText =
                `US$/BRL: R$ ${dados.valor} (${dados.variacao}%)`;

        } catch (error) {

            console.error("Erro dólar:", error);

        }
    }

    atualizarDolar();

    // Atualiza a cada 1 minuto
    setInterval(atualizarDolar, 60000);

    //===NOTICIAS REGIONAIS========
    async function atualizarNoticias() {

    try {

        const response = await fetch('/api/noticias');

        const noticias = await response.json();

        let html = '';

        noticias.forEach((noticia, index) => {

            html += `
                <p>
                    <strong>Notícia ${index + 1}:</strong>
                    ${noticia.titulo}
                </p>
            `;

        });

        document.getElementById('noticias-regionais').innerHTML = html;

    } catch (error) {

        console.error("Erro notícias:", error);

    }
}

atualizarNoticias();

// Atualiza a cada 5 minutos
setInterval(atualizarNoticias, 300000);

//====CLIMATEMPO==============
async function atualizarClima() {

    try {

        const response = await fetch('/api/clima');

        const dados = await response.json();

        document.getElementById('clima-box').innerHTML = `

            <p>
                <strong>${dados.cidade}</strong>
            </p>

            <p>
                ${dados.temperatura}°C
            </p>

            <p>
                ${dados.descricao}
            </p>

        `;

    } catch (error) {

        console.error("Erro clima:", error);

    }
}

atualizarClima();

// Atualiza a cada 10 minutos
setInterval(atualizarClima, 600000);
});

