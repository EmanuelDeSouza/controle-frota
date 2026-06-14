from flask import Blueprint, jsonify, request, session, render_template
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models import db, Item

item_bp = Blueprint('item_bp', __name__)

@item_bp.route('/itens')
def pagina_itens():
    if 'usuario_id' not in session:
        return render_template('login.html')
    return render_template('itens.html')

@item_bp.route('/api/itens/cadastrar', methods=['POST'])
def cadastrar_item():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401

    dados = request.get_json() or {}
    nome = dados.get('nome')
    valor_unitario = dados.get('valor_unitario')

    if not nome or not valor_unitario:
        return jsonify({'error': 'Nome e valor são obrigatórios'}), 400

    novo_item = Item(
        nome=nome,
        valor_unitario=float(valor_unitario),
        categoria=dados.get('categoria')
    )

    try:
        db.session.add(novo_item)
        db.session.commit()
        return jsonify({'message': 'Cadastrado com sucesso'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@item_bp.route('/api/itens', methods=['GET'])
def listar_itens():
    if 'usuario_id' not in session:
        return jsonify([]), 401

    itens = db.session.query(Item).order_by(Item.nome.asc()).all()

    return jsonify([
        {
            "id": i.id,
            "nome": i.nome,
            "valor_unitario": float(i.valor_unitario) if i.valor_unitario else 0.0,
            "categoria": i.categoria
        } for i in itens
    ])

@item_bp.route('/api/gastos/item/<int:id>', methods=['DELETE'])
@item_bp.route('/api/gastos/manutencao/<int:id>', methods=['DELETE'])
def excluir_gasto(id):
    try:
        gasto = Gasto.query.get(id)
        if not gasto:
            return jsonify({"erro": "Gasto não encontrado."}), 404
        
        db.session.delete(gasto)
        db.session.commit()
        return jsonify({"mensagem": "Gasto excluído com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao excluir: {str(e)}"}), 500