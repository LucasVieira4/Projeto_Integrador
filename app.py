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
    atual = db.query(Senha).filter_by(status="em atendimento").order_by(Senha.id.desc()).first()

    # 2. PRÓXIMOS: Aplicando a lógica 2:1 para o JSON
    prio = db.query(Senha).filter(Senha.status == "aguardando", Senha.prioridade > 1).order_by(Senha.prioridade.desc(), Senha.id.asc()).all()
    norm = db.query(Senha).filter(Senha.status == "aguardando", Senha.prioridade == 1).order_by(Senha.id.asc()).all()

    total_chamados = db.query(Senha).filter(Senha.status.in_(['em atendimento', 'finalizado'])).count()

    # Usa a função que você já tem no código
    fila_mista = obter_fila_ordenada(prio, norm, total_chamados)

    # 3. FINALIZADOS: As últimas 5 senhas que já foram atendidas
    finalizados = db.query(Senha).filter_by(status="finalizado").order_by(Senha.id.desc()).limit(10).all()

    res = {
        "atual": {
            "codigo": atual.senha,
            "setor": atual.setor,
            "tipo": atual.tipo
        } if atual else None,
        "proximos": [{"codigo": s.senha, "setor": s.setor} for s in fila_mista[:10]],  # Agora em ordem 2:1
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


@app.route("/api/gerar_senha", methods=['POST'])
def gerar_senha():
    dados = request.json
    setor = dados.get('setor', 'geral')
    # O número (1 a 8) que vem do clique no botão do totem
    prioridade_origem = int(dados.get('prioridade', 8))

    # 1. MAPEAMENTO DE EXIBIÇÃO (O que aparece no ticket)
    prefixos = {1: "I+", 2: "G", 3: "L", 4: "C", 5: "T", 6: "D", 7: "I", 8: "N"}
    nomes = {
        1: "Idoso 80+", 2: "Gestante", 3: "Lactante",
        4: "Criança de Colo", 5: "TEA", 6: "Deficiente",
        7: "Idoso", 8: "Normal"
    }

    # 2. HIERARQUIA DE PESOS (O que o banco usa para ordenar a fila)
    # Aqui definimos que 80+ (ID 1 do totem) tem o maior peso (5)
    pesos_reais = {
        1: 5,  # Idoso 80+ -> Peso Máximo
        5: 4, 6: 4, 7: 4,  # TEA, Deficiente, Idoso 60-79 -> Peso Alto
        2: 3, 3: 3, 4: 3,  # Gestante, Lactante, Colo -> Peso Médio
        8: 1  # Normal -> Peso Mínimo
    }

    prefixo = prefixos.get(prioridade_origem, "N")
    nome_tipo = nomes.get(prioridade_origem, "Normal")
    peso_fila = pesos_reais.get(prioridade_origem, 1)

    # Gera o código (Ex: I+-001 ou N-001)
    codigo = obter_proximo_codigo(prefixo, setor)

    db = Session()
    try:
        nova_senha = Senha(
            senha=codigo,
            tipo=nome_tipo,  # Salva o nome amigável (Ex: "Idoso 80+")
            prioridade=peso_fila,  # SALVA O NÚMERO (5, 4, 3 ou 1) PARA ORDENAÇÃO
            status="aguardando",
            setor=setor,
            servico="Atendimento Geral"
        )
        db.add(nova_senha)
        db.commit()

        print(f">>> SENHA GERADA: {codigo} | TIPO: {nome_tipo} | PESO: {peso_fila}")
        return jsonify({"codigo": codigo, "tipo": nome_tipo})

    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar no banco: {e}")
        return jsonify({"erro": str(e)}), 500
    finally:
        db.close()


@app.route("/api/chamar_proximo/<setor>")
def chamar_proximo(setor):
    db = Session()
    setor = setor.lower()

    try:
        # 1. Conta quantos atendimentos já foram CONCLUÍDOS ou estão EM ANDAMENTO hoje
        # Isso serve como nosso ponteiro do ciclo
        total_ja_chamados = db.query(Senha).filter(
            Senha.setor == setor,
            Senha.status.in_(['em atendimento', 'finalizado'])
        ).count()

        # O próximo atendimento será o número:
        proximo_numero = total_ja_chamados + 1

        proxima = None

        # 2. REGRA DO CICLO (2 Prioritários : 1 Normal)
        # Se o resto da divisão por 3 for 0, é a vez do Normal (atendimentos 3, 6, 9...)
        if proximo_numero % 3 == 0:
            proxima = db.query(Senha).filter_by(
                setor=setor,
                status="aguardando",
                prioridade=1
            ).order_by(Senha.id.asc()).first()

            # Se não houver Normal para cumprir o ciclo, busca qualquer um (Prioritário)
            if not proxima:
                proxima = db.query(Senha).filter_by(setor=setor, status="aguardando") \
                    .order_by(Senha.prioridade.desc(), Senha.id.asc()).first()

        else:
            # É a vez do Prioritário (atendimentos 1, 2, 4, 5, 7, 8...)
            proxima = db.query(Senha).filter(
                Senha.setor == setor,
                Senha.status == "aguardando",
                Senha.prioridade > 1
            ).order_by(Senha.prioridade.desc(), Senha.id.asc()).first()

            # Se não houver Prioritário, busca qualquer um (Normal)
            if not proxima:
                proxima = db.query(Senha).filter_by(setor=setor, status="aguardando") \
                    .order_by(Senha.id.asc()).first()

        # 3. Executa a chamada
        if proxima:
            # Limpa o que estava em atendimento antes
            db.query(Senha).filter_by(setor=setor, status="em atendimento").update({"status": "finalizado"})

            proxima.status = "em atendimento"
            db.commit()
            return jsonify({"codigo": proxima.senha, "tipo": proxima.tipo})

        return jsonify({"erro": "Fila vazia"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        db.close()

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


def obter_fila_ordenada(prioritarios, normais, total_ja_chamados=0):
    fila_final = []
    p_idx = 0
    n_idx = 0

    # Define a posição inicial no ciclo 2:1 baseado em quem já foi chamado
    ponteiro = total_ja_chamados + 1

    while p_idx < len(prioritarios) or n_idx < len(normais):
        # A cada 3 posições (3º, 6º, 9º...), a vez é do Normal
        if ponteiro % 3 == 0:
            if n_idx < len(normais):
                fila_final.append(normais[n_idx])
                n_idx += 1
            elif p_idx < len(prioritarios):
                fila_final.append(prioritarios[p_idx])
                p_idx += 1
        else:
            # Posições 1 e 2 do ciclo são para Prioritários
            if p_idx < len(prioritarios):
                fila_final.append(prioritarios[p_idx])
                p_idx += 1
            elif n_idx < len(normais):
                fila_final.append(normais[n_idx])
                n_idx += 1

        ponteiro += 1

    return fila_final
@app.route('/painel')
def painel():
    db = Session()
    try:

        total_chamados = db.query(Senha).filter(Senha.status.in_(['em atendimento', 'finalizado'])).count()
        # 1. Busca os Prioritários:
        # Ordena PRIMEIRO pelo peso (5, 4, 3) e DEPOIS por quem chegou antes (id)
        prioritarios = db.query(Senha).filter(
            Senha.status == 'aguardando',
            Senha.prioridade > 1
        ).order_by(Senha.prioridade.desc(), Senha.id.asc()).all()

        # 2. Busca os Normais:
        # Ordena apenas por ordem de chegada
        normais = db.query(Senha).filter(
            Senha.status == 'aguardando',
            Senha.prioridade == 1
        ).order_by(Senha.id.asc()).all()

        # 3. Aplica a lógica de intercalação (2 prioritários : 1 normal)
        # Usando a função auxiliar obter_fila_ordenada que você já tem no código
        fila_completa = obter_fila_ordenada(prioritarios, normais, total_chamados)

        # 4. Renderiza o template passando a lista organizada
        # Limitamos aos 10 primeiros para manter o painel limpo
        return render_template('painel.html', proximos=fila_completa[:10])

    except Exception as e:
        print(f"Erro ao carregar painel: {e}")
        return "Erro interno no servidor", 500
    finally:
        # IMPORTANTE: Sempre remover a sessão para liberar conexões com o MySQL
        Session.remove()

@app.teardown_appcontext
def shutdown_session(_=None):
    Session.remove()


@app.route('/finalizar/<int:id>')
def finalizar(id):
    db = Session()
    try:
        senha = db.query(Senha).get(id)
        if senha:
            senha.status = "finalizado"
            db.commit()
            return jsonify({"status": "sucesso"}), 200
        return jsonify({"status": "erro", "mensagem": "Senha não encontrada"}), 404
    except Exception as e:
        db.rollback()
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
    finally:
        Session.remove()

# INICIA O SERVIDOR
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)