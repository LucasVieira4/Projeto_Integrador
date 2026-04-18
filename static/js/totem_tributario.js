async function gerarSenha(prioridade){

    const servico = document.getElementById("servicoSelect").value;

    try{

        const response = await fetch('/api/gerar_senha', {
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body: JSON.stringify({
                setor:'tributario',
                servico:servico,
                prioridade:prioridade
            })
        });

        const data = await response.json();

        if(data.erro){
            alert(data.erro);
        }else{
            alert(`SENHA GERADA: ${data.codigo}`);
        }

    }catch(error){
        alert("Erro de conexão com servidor.");
    }
}