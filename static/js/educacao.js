function atualizarEducacao() {
    fetch('http://192.168.15.4:5000/api/educacao')
    .then(res => res.json())
    .then(data => {
        document.getElementById("aguardando").innerText = data.aguardando;
        document.getElementById("atendimento").innerText = data.atendimento;
        document.getElementById("finalizados").innerText = data.finalizados;
    });
}

setInterval(atualizarEducacao, 5000);
atualizarEducacao();
