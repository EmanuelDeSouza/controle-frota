from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'  
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.Text, nullable=False)
    caminhoes = db.relationship('Caminhao', back_populates='usuario')

# IMPORTANTE: A classe Caminhao deve vir ANTES de Gasto, Abastecimento e Receita
class Caminhao(db.Model):
    __tablename__ = 'caminhao'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    prefixo = db.Column(db.String(5), nullable=False)
    chassi = db.Column(db.String(17), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', back_populates='caminhoes')
    
    # RELACIONAMENTOS EXPLICITOS (Ajuda o SQLAlchemy a mapear as chaves estrangeiras sem erros)
    gastos = db.relationship('Gasto', backref='caminhao', lazy=True)
    abastecimentos = db.relationship('Abastecimento', backref='caminhao', lazy=True)
    receitas = db.relationship('Receita', backref='caminhao', lazy=True)

class Gasto(db.Model):
    __tablename__ = 'gasto'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10,2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhao.id'), nullable=False)

class Abastecimento(db.Model):
    __tablename__='abastecimento'
    id = db.Column(db.Integer, primary_key=True)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhao.id'), nullable=False)
    litros = db.Column(db.Numeric(10,2), nullable=False)
    valor = db.Column(db.Numeric(10,2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    km_atual = db.Column(db.Numeric(8), nullable=False)

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2))
    categoria = db.Column(db.String(50))

class Manutencao(db.Model):
    __tablename__='manutencao'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    km = db.Column(db.Numeric(10, 1), nullable=False)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhao.id'), nullable=False)

class ManutencaoItem(db.Model):
    __tablename__='manutencao_item'
    id = db.Column(db.Integer, primary_key=True)
    manutencao_id = db.Column(db.Integer, db.ForeignKey('manutencao.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantidade = db.Column(db.Numeric(10,2), nullable=False)

class Receita(db.Model):
    __tablename__='receita'
    id = db.Column(db.Integer, primary_key=True)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhao.id'), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False)