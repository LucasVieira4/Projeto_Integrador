from flask import jsonify

@app.route("/api/educacao")
def dados_educacao():
    aguardando = session.query(Senha).filter_by(setor="educacao", status="atendimento").count()

    atendimento = session.query(Senha).filter_by(setor="educacao", status="atendimento").count()

    finalizados = session.query(Senha).filter_by(setor="educacao", status="finalizado")

    return jsonify({
        "aguardando": aguardando,
        "atendimento": atendimento,
        "finalizados": finalizados
    })