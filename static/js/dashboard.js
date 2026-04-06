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
});