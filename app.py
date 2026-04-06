from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Senha, Usuario
from datetime import datetime
from flask_cors import CORS

# CRIA O APP FLASK
app= Flask(__name__)
app.secret_key = 'qms_secret_key_2026'
CORS(app)
# CONEXÃO COM O BANCO
engine = create_engine("mysql+pymysql://root:F%40bio1980@localhost/qms")
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# FUNÇÃO GERAR PRÓXIMO CÒDIGO

def obter_proximo_codigo(prefixo, setor):
    db = Session()
    hoje = datetime.now().date()

    # Busca a última senha do dia filtrando por prefixo e setor
    ultima = db.query(Senha).filter(
        Senha.senha.like(f"{prefixo}-%"),  # Correção: O campo no seu model é 'senha', não 'codigo'
        Senha.setor == setor,
        func.date(Senha.data_emissao) == hoje
    ).order_by(Senha.id.desc()).first()

    numero = 1
    if ultima:
        try:
            # Pega a parte numérica após o hífen
            numero = int(ultima.senha.split('-')[1]) + 1
        except (IndexError, ValueError):
            numero = 1

    return f"{prefixo}-{numero:03d}"

# novas rotas

@app.route('/api/painel_completo')
def painel_completo():
    db = Session()

    # 1. ATUAL: A última senha que mudou para "em atendimento"
    atual = db.query(Senha).filter_by(status="em atendimento") \
        .order_by(Senha.id.desc()).first()

    # 2. PRÓXIMOS: As próximas 5 senhas que estão na fila (aguardando)
    proximos = db.query(Senha).filter_by(status="aguardando") \
        .order_by(Senha.prioridade.asc(), Senha.id.asc()).limit(5).all()

    # 3. FINALIZADOS: As últimas 5 senhas que já foram atendidas
    finalizados = db.query(Senha).filter_by(status="finalizado") \
        .order_by(Senha.id.desc()).limit(5).all()

    res = {
        "atual": {
            "codigo": atual.senha,
            "setor": atual.setor,
            "tipo": atual.tipo
        } if atual else None,
        "proximos": [{"codigo": s.senha, "setor": s.setor} for s in proximos],
        "finalizados": [{"codigo": s.senha, "setor": s.setor} for s in finalizados]
    }

    Session.remove()
    return jsonify(res)

@app.route('/api/ultima_chamada')
def ultima_chamada():

    db = Session()
    senha = db.query(Senha).filter_by(status="em atendimento").order_by(Senha.id.desc()).first()

    if senha:
        res = {
            'codigo': senha.senha,
            'setor': senha.setor,
            'tipo': senha.tipo
        }
        Session.remove()
        return jsonify(res)

    Session.remove()
    return jsonify(None)

@app.route('/api/historico_painel')
def historico_painel():

    db = Session()
    chamadas = db.query(Senha).filter_by(status="em atendimento").order_by(Senha.id.desc()).offset(1).limit(5).all()

    lista = [{'codigo': s.senha, 'setor': s.setor} for s in chamadas]

    Session.remove()
    return jsonify(lista)


@app.route("/api/gerar_senha", methods=['POST'])
def gerar_senha():
    dados = request.json
    setor = dados.get('setor')
    prioridade_num = int(dados.get('prioridade'))# O número (1 a 8) vindo do totem


    prefixos = {1: "I+", 2: "G", 3: "L", 4: "C", 5: "T", 6: "D", 7: "I", 8: "N"}
    tipos = {1: "Idoso 80+", 2: "Gestante", 3: "Lactante", 4: "Criança de Colo", 5: "TEA", 6: "Deficiente", 7: "Idoso",
             8: "Normal"}

    prefixo = prefixos.get(prioridade_num, "N")
    nome_tipo = tipos.get(prioridade_num, "Normal")
    codigo = obter_proximo_codigo(prefixo, setor)

    # CORREÇÃO: Mapeia o número para o que o Banco (Enum) aceita
    # Se for de 1 a 7 (prioritarios), envia 'Prioritario'. Se for 8, 'Normal'.
    prioridade_texto = "Prioritario" if prioridade_num < 8 else "Normal"

    db = Session()
    try:
        nova_senha = Senha(
            senha=codigo,
            tipo=nome_tipo,
            prioridade=prioridade_texto,  # AGORA ENVIA A STRING CORRETA
            status="aguardando",
            setor=setor,
            servico="Atendimento Geral"  # ADICIONADO: Campo obrigatório no seu model
        )
        db.add(nova_senha)
        db.commit()
        res = {"codigo": codigo, "tipo": nome_tipo}
        return jsonify(res)
    except Exception as e:
        db.rollback()
        print(f"erro ao salvar no banco: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/api/chamar_proximo/<setor>")
def chamar_proximo(setor):
    db = Session()
    setor = setor.lower()

    proxima = db.query(Senha).filter_by(setor=setor, status="aguardando").order_by(Senha.prioridade.asc(), Senha.id.asc()).first()

    if proxima:
        db.query(Senha).filter_by(setor=setor, status="em atendimento").update({"status": "finalizado"})

        proxima.status = "em atendimento"
        db.commit()
        return jsonify({"codigo": proxima.senha, "tipo": proxima.tipo})

    return jsonify({"erro": "Fila vazia"}), 404



# --- ROTAS DAS PÁGINAS ---

@app.route("/totem")
def totem():
    return render_template("totem.html")


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/auth", methods=['POST'])
def auth():
    login_form = request.form.get('usuario')
    senha_form = request.form.get('senha')

    db_session = Session()
    user = db_session.query(Usuario).filter_by(login=login_form, senha=senha_form).first()
    db_session.close()

    if user:
        session['usuario_logado'] = user.login
        session['setor'] = user.setor

        return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/api/relatorio/<setor>")
def dados_relatorio(setor):
    with engine.connect() as conexao:
        query = text("SELECT COUNT(*) FROM atendimentos WHERE setor = :setor")
        resultado = conexao.execute(query, {"setor": setor})
        total = resultado.scalar()

    return jsonify({
        'setor': setor,
        'total_atendimentos': total
    })

@app.route("/educacao")
def educacao():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'educacao':
        return redirect(url_for('acesso_negado'))

    return render_template("educacao.html")

@app.route("/saude")
def saude():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'saude':
        return redirect(url_for('acesso_negado'))

    return render_template("saude.html")


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

# ROTA DO DASHBOARD (API)

@app.route("/acesso_negado")
def acesso_negado():
    return render_template("acesso_negado.html")

@app.route("/dashboard")
def dashboard():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")


@app.route("/api/dashboard")
def dados_dashboard():

    if 'usuario_logado' not in session:
        return jsonify({"erro": "Não logado"}), 401

    db = Session()
    setor_user = session.get('setor')

    if not setor_user:
        return jsonify({"erro": "setor não definido"}), 400

    aguardando = db.query(Senha).filter_by(status="aguardando", setor=setor_user).count()
    atendimento = db.query(Senha).filter_by(status="em atendimento", setor=setor_user).count()
    finalizado = db.query(Senha).filter_by(status="finalizado", setor=setor_user).count()

    return jsonify({
        "aguardando": aguardando,
        "atendimento": atendimento,
        "finalizado": finalizado
    })

# painel tv

@app.route("/painel")
def painel_publico():
    # Esta rota não precisa de login, pois ficará na TV da recepção
    return render_template("painel.html")

# resolver problema de limitação de conexões

@app.teardown_appcontext
def shutdown_session(_=None):
    Session.remove()

# INICIA O SERVIDOR
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)