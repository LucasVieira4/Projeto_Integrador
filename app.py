from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Senha, Usuario
from datetime import datetime
from flask_cors import CORS

# =========================
# CONFIGURAÇÃO
# =========================
app = Flask(__name__)
app.secret_key = 'qms_secret_key_2026'
CORS(app)

engine = create_engine("mysql+pymysql://root:F%40bio1980@localhost/qms")
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# =========================
# FUNÇÕES AUXILIARES
# =========================
def obter_proximo_codigo(prefixo, setor):
    db = Session()
    hoje = datetime.now().date()

    ultima = db.query(Senha).filter(
        Senha.senha.like(f"{prefixo}-%"),
        Senha.setor == setor,
        func.date(Senha.data_emissao) == hoje
    ).order_by(Senha.id.desc()).first()

    numero = 1
    if ultima:
        try:
            numero = int(ultima.senha.split('-')[1]) + 1
        except:
            numero = 1

    db.close()
    return f"{prefixo}-{numero:03d}"


def obter_fila_ordenada(prioritarios, normais, total_ja_chamados=0):
    fila_final = []
    p_idx = 0
    n_idx = 0
    ponteiro = total_ja_chamados + 1

    while p_idx < len(prioritarios) or n_idx < len(normais):
        if ponteiro % 3 == 0:
            if n_idx < len(normais):
                fila_final.append(normais[n_idx])
                n_idx += 1
            elif p_idx < len(prioritarios):
                fila_final.append(prioritarios[p_idx])
                p_idx += 1
        else:
            if p_idx < len(prioritarios):
                fila_final.append(prioritarios[p_idx])
                p_idx += 1
            elif n_idx < len(normais):
                fila_final.append(normais[n_idx])
                n_idx += 1

        ponteiro += 1

    return fila_final


# =========================
# APIs
# =========================

@app.route('/api/painel_completo')
def painel_completo():
    db = Session()

    try:
        atual = db.query(Senha).filter_by(status="em atendimento") \
            .order_by(Senha.id.desc()).first()

        prio = db.query(Senha).filter(
            Senha.status == "aguardando",
            Senha.prioridade > 1
        ).order_by(Senha.prioridade.desc(), Senha.id.asc()).all()

        norm = db.query(Senha).filter(
            Senha.status == "aguardando",
            Senha.prioridade == 1
        ).order_by(Senha.id.asc()).all()

        total = db.query(Senha).filter(
            Senha.status.in_(['em atendimento', 'finalizado'])
        ).count()

        fila = obter_fila_ordenada(prio, norm, total)

        finalizados = db.query(Senha).filter_by(status="finalizado") \
            .order_by(Senha.id.desc()).limit(10).all()

        return jsonify({
            "atual": {
                "codigo": atual.senha,
                "setor": atual.setor,
                "tipo": atual.tipo
            } if atual else None,
            "proximos": [{"codigo": s.senha, "setor": s.setor} for s in fila[:10]],
            "finalizados": [{"codigo": s.senha, "setor": s.setor} for s in finalizados]
        })

    finally:
        db.close()

@app.route('/painel')
def painel():
    db = Session()
    try:
        total = db.query(Senha).filter(
            Senha.status.in_(['em atendimento', 'finalizado'])
        ).count()

        prio = db.query(Senha).filter(
            Senha.status == 'aguardando',
            Senha.prioridade > 1
        ).order_by(Senha.prioridade.desc(), Senha.id.asc()).all()

        norm = db.query(Senha).filter(
            Senha.status == 'aguardando',
            Senha.prioridade == 1
        ).order_by(Senha.id.asc()).all()

        fila = obter_fila_ordenada(prio, norm, total)

        return render_template('painel.html', proximos=fila[:10])

    finally:
        db.close()

@app.route('/totem')
def totem():
    return render_template("totem.html")

@app.route("/saude")
def saude():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'saude':
        return redirect(url_for('acesso_negado'))

    return render_template("saude.html")

@app.route("/educacao")
def educacao():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'educacao':
        return redirect(url_for('acesso_negado'))

    return render_template("educacao.html")


@app.route("/tributario")
def tributario():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'tributario':
        return redirect(url_for('acesso_negado'))

    return render_template("tributario.html")


@app.route('/relatorio')
def relatorio():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    return render_template("relatorio.html")


@app.route("/api/gerar_senha", methods=['POST'])
def gerar_senha():
    dados = request.json
    setor = dados.get('setor', 'saude')
    prioridade_origem = int(dados.get('prioridade', 8))

    prefixos = {1: "I+", 2: "G", 3: "L", 4: "C", 5: "T", 6: "D", 7: "I", 8: "N"}
    nomes = {
        1: "Idoso 80+", 2: "Gestante", 3: "Lactante",
        4: "Criança de Colo", 5: "TEA", 6: "Deficiente",
        7: "Idoso", 8: "Normal"
    }

    pesos = {1: 5, 5: 4, 6: 4, 7: 4, 2: 3, 3: 3, 4: 3, 8: 1}

    codigo = obter_proximo_codigo(prefixos[prioridade_origem], setor)

    db = Session()
    try:
        nova = Senha(
            senha=codigo,
            tipo=nomes[prioridade_origem],
            prioridade=pesos[prioridade_origem],
            status="aguardando",
            setor=setor,
            servico="clinico geral"
        )
        db.add(nova)
        db.commit()

        return jsonify({"codigo": codigo, "tipo": nomes[prioridade_origem]})
    except Exception as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        db.close()


@app.route("/api/chamar_proximo/<setor>")
def chamar_proximo(setor):
    db = Session()
    setor = setor.lower()

    try:
        total = db.query(Senha).filter(
            Senha.setor == setor,
            Senha.status.in_(['em atendimento', 'finalizado'])
        ).count()

        proximo_num = total + 1

        if proximo_num % 3 == 0:
            proxima = db.query(Senha).filter_by(
                setor=setor, status="aguardando", prioridade=1
            ).order_by(Senha.id.asc()).first()
        else:
            proxima = db.query(Senha).filter(
                Senha.setor == setor,
                Senha.status == "aguardando",
                Senha.prioridade > 1
            ).order_by(Senha.prioridade.desc(), Senha.id.asc()).first()

        if not proxima:
            proxima = db.query(Senha).filter_by(
                setor=setor, status="aguardando"
            ).order_by(Senha.id.asc()).first()

        if proxima:
            db.query(Senha).filter_by(
                setor=setor, status="em atendimento"
            ).update({"status": "finalizado"})

            proxima.status = "em atendimento"
            db.commit()

            return jsonify({"codigo": proxima.senha, "tipo": proxima.tipo})

        return jsonify({"erro": "Fila vazia"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        db.close()


@app.route("/api/dashboard")
def dashboard_api():
    if 'usuario_logado' not in session:
        return jsonify({"erro": "Não logado"}), 401

    db = Session()
    try:
        setor = session.get('setor')

        return jsonify({
            "aguardando": db.query(Senha).filter_by(setor=setor, status="aguardando").count(),
            "atendimento": db.query(Senha).filter_by(setor=setor, status="em atendimento").count(),
            "finalizado": db.query(Senha).filter_by(setor=setor, status="finalizado").count(),

            "contagem_clinico": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="clinico geral").count(),

            "contagem_pediatria": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="pediatria").count(),

            "contagem_ortopedia": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="ortopedia").count(),

            "contagem_odontologia": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="odontologia").count(),

            "contagem_vacinas": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="vacinas").count()

        })
    finally:
        db.close()


@app.route("/api/educacao")
def dados_educacao():
    db = Session()
    try:
        return jsonify({
            "aguardando": db.query(Senha).filter_by(setor="educacao", status="aguardando").count(),
            "atendimento": db.query(Senha).filter_by(setor="educacao", status="em atendimento").count(),
            "finalizados": db.query(Senha).filter_by(setor="educacao", status="finalizado").count()
        })
    finally:
        db.close()

# ==========================
# ROTA CADASTRAR ATENDIMENTO
# ==========================

@app.route('/api/cadastrar_atendimento', methods=['POST'])
def cadastrar_atendimento():
    dados = request.json
    codigo = dados.get('codigo')
    senha_id = dados.get('senha_id')
    especialidade = dados.get('especialidade')  # Certifique-se que o nome bate com o banco
    nome = dados.get('nome')
    filiacao = dados.get('filiacao')
    nascimento = dados.get('nascimento')
    endereco = dados.get('endereco')

    db = Session()

    try:
        atendimento = db.query(Senha).filter_by(senha=codigo).first()

        if atendimento:
            atendimento.status = 'finalizado'
            atendimento.servico = especialidade
            atendimento.nome_paciente = nome
            atendimento.filiacao = filiacao
            atendimento.endereco = endereco
            atendimento.data_fim_atendimento = datetime.now()

            db.commit()
            return jsonify({"status":"sucesso"}), 200
        return jsonify({"status":"erro"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        db.close()


# =========================
# ROTAS WEB
# =========================

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/auth", methods=['POST'])
def auth():
    db = Session()
    user = db.query(Usuario).filter_by(
        login=request.form.get('usuario'),
        senha=request.form.get('senha')
    ).first()
    db.close()

    if user:
        session['usuario_logado'] = user.login
        session['setor'] = user.setor
        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))


@app.route("/dashboard")
def dashboard():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# =========================
# FINAL
# =========================
@app.teardown_appcontext
def shutdown_session(_=None):
    Session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)