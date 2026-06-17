from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash  
import os
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from models import db, Usuario, Caminhao, Gasto, Abastecimento, Item, Manutencao, ManutencaoItem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))  

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
IS_PRODUCTION = os.environ.get('RENDER') is not None

# ==================== CONFIGURAÇÃO DO BANCO DE DADOS ====================
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'projetosema') 
DB_HOST = os.environ.get('DB_HOST', 'localhost')   
DB_PORT = os.environ.get('DB_PORT', '5432')       
DB_NAME = os.environ.get('DB_NAME', 'projetofrota')

senha_encoded = quote_plus(DB_PASSWORD)
RENDER_DATABASE_URL = os.environ.get('DATABASE_URL')

if RENDER_DATABASE_URL:
    SQLALCHEMY_URL = RENDER_DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    if 'sslmode' not in SQLALCHEMY_URL:
        if '?' in SQLALCHEMY_URL:
            SQLALCHEMY_URL += '&sslmode=require'
        else:
            SQLALCHEMY_URL += '?sslmode=require'
else:
    SQLALCHEMY_URL = f'postgresql://{DB_USER}:{senha_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True
}

# ==================== CONFIGURAÇÃO DE SEGURANÇA E SESSÃO ====================
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'uma_chave_secreta_para_flash')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=IS_PRODUCTION 
)
db.init_app(app)

# ==================== ROTAS DE AUTENTICAÇÃO GERAL ====================
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']
        usuario_bd = Usuario.query.filter(
            (Usuario.nome == usuario_form) | (Usuario.email == usuario_form)
        ).first()
        if usuario_bd and check_password_hash(usuario_bd.senha, senha_form):
            session['usuario_id'] = usuario_bd.id
            session['usuario_nome'] = usuario_bd.nome
            # CORREÇÃO: Aponta para a rota 'dashboard' de dentro do blueprint 'dashboard_bp'
            return redirect(url_for('dashboard_bp.dashboard'))
        return render_template('login.html', erro='Usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']
        if senha != confirmar_senha:
            flash('As senhas não coincidem.')
            return render_template('cadastro.html')
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.')
            return render_template('cadastro.html')
        novo_usuario = Usuario(
            nome=nome, email=email, senha=generate_password_hash(senha)
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso.')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))

# ==================== ROTAS DE RENDERIZAÇÃO DE TEMPLATES ====================
@app.route('/dashboard')
def dashboard():  
    return render_template('dashboard.html')

@app.route('/caminhoes')
def caminhoes():
    return render_template('caminhao.html')

@app.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')

# ==================== MIDDLWARE DE VERIFICAÇÃO DE ACESSO ====================
@app.before_request
def verificar_autenticacao_global():
    if request.path.startswith('/static/'):
        return
    rotas_publicas = ['login', 'cadastro']
    if not request.endpoint or request.endpoint in rotas_publicas:
        return
    if 'usuario_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({"erro": "Acesso não autorizado. Faça login."}), 401
        return redirect(url_for('login'))

# Verificação e criação automática das tabelas em desenvolvimento local
with app.app_context():
    if not IS_PRODUCTION:
        db.create_all()
        print("Tabelas verificadas/criadas com sucesso no banco local!")
    
# ==================== REGISTRO DOS BLUEPRINTS ====================
from modulos.caminhao_rotas import caminhao_bp
from modulos.item_rotas import item_bp
from modulos.relatorio_rotas import relatorio_bp
from modulos.dashboard_rotas import dashboard_bp

app.register_blueprint(caminhao_bp)
app.register_blueprint(item_bp)
app.register_blueprint(relatorio_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=not IS_PRODUCTION)