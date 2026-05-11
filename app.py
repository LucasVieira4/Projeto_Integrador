from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Senha, Usuario
from datetime import datetime
from flask_cors import CORS

import requests

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

#=======COTAÇÃO DOLAR======
@app.route('/api/dolar')
def api_dolar():
    try:
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"

        response = requests.get(url)
        dados = response.json()

        valor = dados['USDBRL']['bid']
        variacao = dados['USDBRL']['pctChange']

        return jsonify({
            'valor': valor,
            'variacao': variacao
        })

    except Exception as e:
        return jsonify({
            'erro': str(e)
        }), 500
#=====Noticias Regionais====
@app.route('/api/noticias')
def api_noticias():

    try:

        API_KEY = "047b1a364668e9439332c6e9412bc505"

        url = f"https://gnews.io/api/v4/top-headlines?lang=pt&country=br&max=3&apikey={API_KEY}"

        response = requests.get(url)

        dados = response.json()

        noticias = []

        for noticia in dados['articles']:

            noticias.append({
                'titulo': noticia['title']
            })

        return jsonify(noticias)

    except Exception as e:

        return jsonify({
            'erro': str(e)
        }), 500
#=======Climatempo==========
@app.route('/api/clima')
def api_clima():

    try:

        # Coordenadas de São Paulo
        latitude = -23.55
        longitude = -46.63

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&current=temperature_2m"
        )

        response = requests.get(url)

        dados = response.json()

        temperatura = dados['current']['temperature_2m']

        return jsonify({

            'cidade': 'São Paulo',
            'temperatura': temperatura,
            'descricao': 'Tempo atualizado'

        })

    except Exception as e:

        return jsonify({
            'erro': str(e)
        }), 500
#=====Painel Chamadas=======

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
      #=====ROTAS TOTENS=======
@app.route('/totem')
def totem():
    return render_template("totem.html")

@app.route('/totem/<setor>')
def totem_setor(setor):
    setores_validos = ['saude', 'educacao', 'tributario']
    if setor not in setores_validos:
        return redirect(url_for('totem'))
    return render_template(f"totem_{setor}.html", setor=setor)

#======logar-saude========
@app.route("/saude")
def saude():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'saude':
        return redirect(url_for('acesso_negado'))

    return render_template("saude.html")
#======logar-educacao==========
@app.route("/educacao")
def educacao():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'educacao':
        return redirect(url_for('acesso_negado'))

    return render_template("educacao.html")

#==========logar-tributario========
@app.route("/tributario")
def tributario():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    if session.get('setor') != 'tributario':
        return redirect(url_for('acesso_negado'))

    return render_template("tributario.html")

#=====relatorio=========
@app.route('/relatorio')
def relatorio():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    return render_template('relatorio.html', setor='saude')
#=======relatorio por setor==========
@app.route("/api/diario/<setor>")
def api_diario(setor):

    db = Session()

    try:

        dados = db.execute(text("""
            SELECT DATE(data_emissao) as dia,
                   COUNT(*) as total
            FROM atendimentos
            WHERE setor = :setor
            GROUP BY DATE(data_emissao)
            ORDER BY dia
        """), {"setor": setor}).fetchall()

        labels = []
        valores = []

        for dia, total in dados:
            labels.append(dia.strftime('%d/%m'))
            valores.append(total)

        return jsonify({
            "labels": labels,
            "valores": valores
        })

    finally:
        db.close()
#===============SAUDE================
@app.route('/relatorio/saude')
def relatorio_saude():

    if session.get('setor') != 'saude':
        return redirect(url_for('acesso_negado'))

    return render_template(
        'relatorio.html',
        setor='saude'
    )
#==============EDUCACAO==================
@app.route('/relatorio/educacao')
def relatorio_educacao():

    if session.get('setor') != 'educacao':
        return redirect(url_for('acesso_negado'))

    return render_template(
        'relatorio.html',
        setor='educacao'
    )
#=============TRIBUTARIO=================
@app.route('/relatorio/tributario')
def relatorio_tributario():

    if session.get('setor') != 'tributario':
        return redirect(url_for('acesso_negado'))

    return render_template(
        'relatorio.html',
        setor='tributario'
    )
#========STATUS GERAL====================
@app.route("/api/status/geral")
def api_status_geral():
    db = Session()
    try:
        dados = db.execute(text("""
            SELECT status, COUNT(*) as total
            FROM atendimentos
            GROUP BY status
        """)).fetchall()

        resultado = {
            "aguardando": 0,
            "atendimento": 0,
            "finalizado": 0
        }

        for status, total in dados:
            if status == "aguardando":
                resultado["aguardando"] = total
            elif status == "em atendimento":
                resultado["atendimento"] = total
            elif status == "finalizado":
                resultado["finalizado"] = total

        return jsonify(resultado)

    finally:
        db.close()
#======Rota Status por setor=============
@app.route("/api/status")
def api_status():
    db = Session()
    try:
        setor = session.get('setor')

        dados = db.execute(text("""
            SELECT status, COUNT(*)
            FROM atendimentos
            WHERE setor = :setor
            GROUP BY status
        """), {"setor": setor}).fetchall()

        resultado = {
            "aguardando": 0,
            "atendimento": 0,
            "finalizado": 0
        }

        for status, total in dados:
            if status == "aguardando":
                resultado["aguardando"] = total
            elif status == "em atendimento":
                resultado["atendimento"] = total
            elif status == "finalizado":
                resultado["finalizado"] = total

        return jsonify(resultado)

    finally:
        db.close()
#=======Rota para dinamizar gráficos=====
@app.route("/api/pizza/<setor>")
def api_pizza(setor):
    db = Session()

    try:
        if setor == "saude":
            dados = {"Clinico Geral": db.query(Senha).filter_by(setor= "saude", status= "finalizado", servico= "clinico geral").count(),
                     "Pediatria": db.query(Senha).filter_by(setor="saude", status= "finalizado", servico= "pediatria").count(),
                     "Ortopedia": db.query(Senha).filter_by(setor= "saude", status= "finalizado", servico= "ortopedia").count(),
                     "Odontologia": db.query(Senha).filter_by(setor= "saude", status= "finalizado", servico= "odontologia").count(),
                     "Vacinas": db.query(Senha).filter_by(setor= "saude", status= "finalizado", servico= "vacinas").count()
            }
        elif setor == "tributario":
            dados = {"IPTU": db.query(Senha).filter_by(setor= "tributario", status= "finalizado", servico= "iptu").count(),
                     "ISS": db.query(Senha).filter_by(setor= "tributario", status= "finalizado", servico= "iss").count(),
                     "Alvará": db.query(Senha).filter_by(setor= "tributario", status= "finalizado", servico= "alvara").count(),
                     "Divida": db.query(Senha).filter_by(setor="tributario", status= "finalizado", servico= "divida").count(),
                     "Certidões": db.query(Senha).filter_by(setor= "tributario", status= "finalizado", servico= "certidoes").count(),
                     "Cadastro": db.query(Senha).filter_by(setor= "tributario", status= "finalizado", servico= "cadastro").count()
            }
        elif setor == "educacao":
            dados = {"Matrículas": db.query(Senha).filter_by(setor= "educacao", status= "finalizado", servico= "matriculas").count(),
                     "Documentos": db.query(Senha).filter_by(setor= "educacao", status= "finalizado", servico= "documentos").count(),
                     "Transporte": db.query(Senha).filter_by(setor= "educacao", status= "finalizado", servico= "transporte").count(),
                     "Creches": db.query(Senha).filter_by(setor= "educacao", status= "finalizado", servico= "creches").count(),
                     "Inclusão": db.query(Senha).filter_by(setor= "educacao", status= "finalizado", servico= "inclusao").count(),
                     "Geral": db.query(Senha).filter_by(setor= "educacao", status= "finalizado", servico= "geral").count()
            }
        else:
            dados = {}

        return jsonify(dados)
    finally:
        db.close()





#=======SENHAS==========
@app.route("/api/gerar_senha", methods=['POST'])
def gerar_senha():
    dados = request.json

    setor = dados.get('setor', 'saude').lower()
    servico = dados.get('servico', 'clinico geral').lower()
    print("servico =", servico)
    prioridade_origem = int(dados.get('prioridade', 8))

    prefixos = {
        1: "I+",
        2: "G",
        3: "L",
        4: "C",
        5: "T",
        6: "D",
        7: "I",
        8: "N"
    }

    nomes = {
        1: "Idoso 80+",
        2: "Gestante",
        3: "Lactante",
        4: "Criança de Colo",
        5: "TEA",
        6: "Deficiente",
        7: "Idoso",
        8: "Normal"
    }

    pesos = {
        1: 5,
        5: 4,
        6: 4,
        7: 4,
        2: 3,
        3: 3,
        4: 3,
        8: 1
    }

    codigo = obter_proximo_codigo(prefixos[prioridade_origem], setor)

    db = Session()

    try:
        nova = Senha(
            senha=codigo,
            tipo=nomes[prioridade_origem],
            prioridade=pesos[prioridade_origem],
            status="aguardando",
            setor=setor,
            servico=servico
        )

        db.add(nova)
        db.commit()

        return jsonify({
            "codigo": codigo,
            "tipo": nomes[prioridade_origem]
        })

    except Exception as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        db.close()
#=====funcionalidade interna dos dashboard========
@app.route("/api/chamar_proximo/<setor>/<servico>")
def chamar_proximo(setor, servico):
    db = Session()

    setor = setor.lower()
    servico = servico.lower()

    try:
        # ==========================================
        # 1️⃣ FINALIZA atendimento atual
        # ==========================================
        atual = db.query(Senha).filter(
            Senha.setor == setor,
            Senha.servico == servico,
            Senha.status == "em atendimento"
        ).first()

        if atual:
            atual.status = "finalizado"

        # ==========================================
        # 2️⃣ DEFINE número da próxima chamada
        # regra 2 prioritários para 1 normal
        # ==========================================
        proximo_num = db.query(Senha).filter(
            Senha.setor == setor,
            Senha.servico == servico,
            Senha.status.in_(["em atendimento", "finalizado"])
        ).count() + 1

        # ==========================================
        # 3️⃣ REGRA DE PRIORIDADE
        # atendimento 3,6,9... = normal
        # demais = prioritário
        # ==========================================
        if proximo_num % 3 == 0:

            # normal
            proxima = db.query(Senha).filter(
                Senha.setor == setor,
                Senha.servico == servico,
                Senha.status == "aguardando",
                Senha.prioridade == 1
            ).order_by(Senha.id.asc()).first()

        else:

            # prioritário
            proxima = db.query(Senha).filter(
                Senha.setor == setor,
                Senha.servico == servico,
                Senha.status == "aguardando",
                Senha.prioridade > 1
            ).order_by(
                Senha.prioridade.desc(),
                Senha.id.asc()
            ).first()

        # ==========================================
        # 4️⃣ FALLBACK
        # ==========================================
        if not proxima:
            proxima = db.query(Senha).filter(
                Senha.setor == setor,
                Senha.servico == servico,
                Senha.status == "aguardando"
            ).order_by(Senha.id.asc()).first()

        # ==========================================
        # 5️⃣ CHAMA próxima senha
        # ==========================================
        if proxima:
            proxima.status = "em atendimento"

            db.commit()

            return jsonify({
                "codigo": proxima.senha,
                "servico": proxima.servico
            })

        # ==========================================
        # 6️⃣ FILA VAZIA
        # salva finalização da última senha
        # ==========================================
        db.commit()

        return jsonify({"erro": "Fila vazia"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        db.close()
#======rota especifica dash saude===========
@app.route("/api/chamar_proximo/saude")
def chamar_proximo_saude():
    db = Session()

    try:
        proxima = db.query(Senha).filter(
            Senha.setor == "saude",
            Senha.status == "aguardando"
        ).order_by(
            Senha.prioridade.desc(),
            Senha.id.asc()
        ).first()

        if not proxima:
            return jsonify({"erro": "Fila vazia"}), 404

        proxima.status = "em atendimento"
        db.commit()

        return jsonify({
            "codigo": proxima.senha,
            "tipo": proxima.tipo
        })

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
                #=====SAUDE===========================
            "contagem_clinico": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="clinico geral").count(),

            "contagem_pediatria": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="pediatria").count(),

            "contagem_ortopedia": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="ortopedia").count(),

            "contagem_odontologia": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="odontologia").count(),

            "contagem_vacinas": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="vacinas").count(),
                #======TRIBUTARIO=======================
            "aguardando_iptu": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="iptu").count(),
            "contagem_iptu": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="iptu").count(),

            "aguardando_iss": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="iss").count(),
            "contagem_iss": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="iss").count(),

            "aguardando_alvara": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="alvara").count(),
            "contagem_alvara": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="alvara").count(),

            "aguardando_divida": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="divida").count(),
            "contagem_divida": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="divida").count(),

            "aguardando_certidoes": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="certidoes").count(),
            "contagem_certidoes": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="certidoes").count(),

            "aguardando_cadastro": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="cadastro").count(),
            "contagem_cadastro": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="cadastro").count(),
                 #========EDUCACAO=======================
            "aguardando_matriculas": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="matriculas").count(),
            "contagem_matriculas": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="matriculas").count(),

            "aguardando_documentos": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="documentos").count(),
            "contagem_documentos": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="documentos").count(),

            "aguardando_transporte": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="transporte").count(),
            "contagem_transporte": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="transporte").count(),

            "aguardando_creches": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="creches").count(),
            "contagem_creches": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="creches").count(),

            "aguardando_inclusao": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="inclusao").count(),
            "contagem_inclusao": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="inclusao").count(),

            "aguardando_geral": db.query(Senha).filter_by(setor=setor, status="aguardando", servico="geral").count(),
            "contagem_geral": db.query(Senha).filter_by(setor=setor, status="finalizado", servico="geral").count()
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

#===========rotas-mobile==============
#============login====================

@app.route('/mobile/login', methods=['GET', 'POST'])
def mobile_login():

    if request.method == 'POST':

        cpf = request.form['cpf']
        senha = request.form['senha']

        # validar usuário futuramente

        return redirect(url_for('mobile_saude'))

    return render_template('mobile/login_mobile.html')

#==============agendamento============================
#========agend_saude==================================
@app.route('/mobile/saude')
def mobile_saude():

    return render_template('mobile/agendamento_mobile.html')
#================agend_educacao==========================
@app.route('/mobile/educacao')
def mobile_educacao():

    return render_template('mobile/agendamento_educacao.html')
#================agend_tributario========================
@app.route('/mobile/tributario')
def mobile_tributario():

    return render_template('mobile/agendamento_tributario.html')
#========gravar dados do agendamento============
@app.route('/mobile/agendar', methods=['POST'])
def mobile_agendar():

    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    especialidade = request.form.get('especialidade')
    data = request.form.get('data')
    horario = request.form.get('horario')

    prioridade_origem = int(request.form.get('prioridade', 8))

    setor = "saude"

    # detectar setor automaticamente
    if especialidade in [
        'matriculas',
        'documentos',
        'transporte',
        'creches',
        'inclusao',
        'geral'
    ]:
        setor = "educacao"

    elif especialidade in [
        'iptu',
        'iss',
        'alvara',
        'divida',
        'certidoes',
        'cadastro'
    ]:
        setor = "tributario"

    prefixos = {
        1: "I+",
        2: "G",
        3: "L",
        4: "C",
        5: "T",
        6: "D",
        7: "I",
        8: "N"
    }

    nomes = {
        1: "Idoso 80+",
        2: "Gestante",
        3: "Lactante",
        4: "Criança de Colo",
        5: "TEA",
        6: "Deficiente",
        7: "Idoso",
        8: "Normal"
    }

    pesos = {
        1: 5,
        5: 4,
        6: 4,
        7: 4,
        2: 3,
        3: 3,
        4: 3,
        8: 1
    }

    codigo = obter_proximo_codigo(
        prefixos[prioridade_origem],
        setor
    )

    db = Session()

    try:

        nova = Senha(
            senha=codigo,
            tipo=nomes[prioridade_origem],
            prioridade=pesos[prioridade_origem],
            status="aguardando",
            setor=setor,
            servico=especialidade,
            origem="remoto",
            nome_paciente=nome
        )

        db.add(nova)
        db.commit()

        return f"""
        <h2>Agendamento realizado com sucesso!</h2>

        <p><strong>Senha:</strong> {codigo}</p>
        <p><strong>Nome:</strong> {nome}</p>
        <p><strong>Setor:</strong> {setor}</p>
        <p><strong>Serviço:</strong> {especialidade}</p>
        <p><strong>Data:</strong> {data}</p>
        <p><strong>Horário:</strong> {horario}</p>
        """

    except Exception as e:

        db.rollback()
        return f"Erro: {str(e)}"

    finally:
        db.close()

# =========================
# FINAL
# =========================
@app.teardown_appcontext
def shutdown_session(_=None):
    Session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)