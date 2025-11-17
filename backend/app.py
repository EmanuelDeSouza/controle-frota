from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import os
from urllib.parse import quote_plus
from flask import jsonify
from datetime import datetime, timedelta
import psycopg2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))  

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)


DB_USER = 'postgres'
DB_PASSWORD = 'projetosema'
DB_HOST = 'localhost'  
DB_PORT = '5432'       
DB_NAME = 'projetofrota'

senha_encoded = quote_plus(DB_PASSWORD)

RENDER_DATABASE_URL = os.environ.get('DATABASE_URL')

if RENDER_DATABASE_URL:
    # Substitui 'postgres' por 'postgresql' para garantir compatibilidade com SQLAlchemy
    SQLALCHEMY_URL = RENDER_DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Usa a configuração local se a variável de ambiente não existir
    SQLALCHEMY_URL = f'postgresql://{DB_USER}:{senha_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'uma_chave_secreta_para_flash'

db = SQLAlchemy(app)


class Usuario(db.Model):
    __tablename__ = 'usuario'  
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

    caminhoes = db.relationship('Caminhao', back_populates='usuario')

class Caminhao(db.Model):
    __tablename__ = 'caminhao'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='caminhoes')

class Gasto(db.Model):
    __tablename__ = 'gasto'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhao.id'), nullable=False)

    caminhao = db.relationship('Caminhao', backref=db.backref('gastos', lazy=True))

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        
        usuario_bd = Usuario.query.filter(
            (Usuario.nome == usuario_form) | (Usuario.email == usuario_form)
        ).first()

        
        if usuario_bd and usuario_bd.senha == senha_form:
            session['usuario_id'] = usuario_bd.id
            session['usuario_nome'] = usuario_bd.nome
            return redirect(url_for('principal'))

        # Se não encontrou ou senha incorreta
        erro = 'Usuário ou senha incorretos.'
        return render_template('login.html', erro=erro)

    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.")
    return redirect(url_for('login'))

@app.route('/principal')
def principal():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('pagprincipal.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']
        # Verificar se email já existe para evitar duplicidade
        if senha != confirmar_senha:
            flash('As senhas não coincidem.')
            return render_template('cadastro.html')
        
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Email já cadastrado. Por favor, faça login ou use outro email.')
            return render_template('cadastro.html')
       
        # Criar novo usuário
        novo_usuario = Usuario(nome=nome, email=email, senha=senha)  
       
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso. Faça login.')
        return redirect(url_for('login'))
    return render_template('cadastro.html')


@app.route('/api/caminhoes', methods=['GET'])
def listar_caminhoes():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    usuario_id = session['usuario_id']
    caminhoes = Caminhao.query.filter_by(usuario_id=usuario_id).all()

    lista = [
        {
            'id': c.id,
            'placa': c.placa,
            'modelo': c.modelo,
            'fabricante': c.fabricante,
            'ano': c.ano
        }
        for c in caminhoes
    ]
    return jsonify(lista)


@app.route('/api/caminhoes', methods=['POST'])
def cadastrar_caminhao():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    dados = request.get_json()
    placa = dados.get('placa')
    modelo = dados.get('modelo')
    fabricante = dados.get('fabricante')
    ano = dados.get('ano')

    if not placa or not modelo or not fabricante or not ano:
        return jsonify({'erro': 'Campos obrigatórios ausentes'}), 400

    cam_existente = Caminhao.query.filter_by(placa=placa).first()
    if cam_existente:
        return jsonify({'erro': 'Caminhão já cadastrado'}), 400

    novo_cam = Caminhao(
        placa=placa,
        modelo=modelo,
        fabricante=fabricante,
        ano=ano,
        usuario_id=session['usuario_id']
    )
    db.session.add(novo_cam)
    db.session.commit()

    return jsonify({'mensagem': 'Caminhão cadastrado com sucesso!'}), 201

@app.route('/api/caminhoes/<int:id>', methods=['DELETE'])
def excluir_caminhao(id):
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'erro': 'Caminhão não encontrado'}), 404

    db.session.delete(caminhao)
    db.session.commit()
    return jsonify({'mensagem': 'Caminhão excluído com sucesso!'}), 200

@app.route('/api/caminhoes/<int:caminhao_id>/gastos', methods=['POST'])
def adicionar_gasto(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=caminhao_id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'error': 'Caminhão não encontrado'}), 404

    data = request.get_json()
    descricao = data.get('descricao')
    valor = data.get('valor')
    data_gasto = data.get('data')

    if not descricao or not valor or not data_gasto:
        return jsonify({'error': 'Campos incompletos!'}), 400

    try:
        data_formatada = datetime.strptime(data_gasto, '%Y-%m-%d')
        novo_gasto = Gasto(
            caminhao_id=caminhao_id,
            descricao=descricao,
            valor=float(valor),
            data=data_formatada
        )
        db.session.add(novo_gasto)
        db.session.commit()
        return jsonify({'message': 'Gasto adicionado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao salvar gasto: {str(e)}'}), 500
    
@app.route('/api/caminhoes/<int:caminhao_id>/gastos', methods=['GET'])
def listar_gastos(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=caminhao_id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'error': 'Caminhão não encontrado'}), 404

    gastos = Gasto.query.filter_by(caminhao_id=caminhao_id).all()
    lista = [
        {
            'id': g.id,
            'valor': float(g.valor),
            'descricao': g.descricao,
            'data': g.data.strftime('%Y-%m-%d')
        }
        for g in gastos
    ]
    return jsonify(lista)

@app.route('/api/relatorio/gastos_detalhado', methods=['GET'])
def relatorio_gastos_detalhado():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')

    if not data_inicial or not data_final:
        return jsonify({'error': 'Datas são obrigatórias'}), 400

    try:
        d_ini = datetime.strptime(data_inicial, "%Y-%m-%d")
        # acrescenta 1 dia ao fim e usa comparação estrita (<) para incluir todo o dia_final
        d_fim = datetime.strptime(data_final, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}), 400

    usuario_id = session['usuario_id']

    gastos = (
        db.session.query(Gasto, Caminhao)
        .join(Caminhao, Gasto.caminhao_id == Caminhao.id)
        .filter(Caminhao.usuario_id == usuario_id)
        .filter(Gasto.data >= d_ini)   
        .filter(Gasto.data <= d_fim)
        .order_by(Gasto.data.desc())
        .all()
    )

    resposta = [
        {
            "placa": c.placa,
            "descricao": g.descricao,
            "data": g.data.strftime("%Y-%m-%d") if isinstance(g.data, (datetime,)) else str(g.data),
            "valor": float(g.valor)
        }
        for g, c in gastos
    ]

    return jsonify(resposta)

# ===== MAIN =====
if __name__ == '__main__':
    app.run(debug=True)
