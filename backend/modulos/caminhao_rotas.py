from flask import Blueprint, jsonify, request, session
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models import db, Caminhao, Gasto, Abastecimento, Receita

caminhao_bp = Blueprint('caminhao_bp', __name__)

@caminhao_bp.route('/api/caminhoes', methods=['GET'])
def listar_caminhoes():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    usuario_id = session['usuario_id']
    caminhoes = Caminhao.query.filter_by(usuario_id=usuario_id).all()
    return jsonify([{
        'id': c.id, 'placa': c.placa, 'modelo': c.modelo,
        'fabricante': c.fabricante, 'ano': c.ano,
        'prefixo': c.prefixo, 'chassi': c.chassi
    } for c in caminhoes])

@caminhao_bp.route('/api/caminhoes/<int:id>', methods=['GET'])
def obter_caminhao(id):
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'erro': 'Caminhão não encontrado'}), 404

    return jsonify({
        'id': caminhao.id, 'placa': caminhao.placa, 'modelo': caminhao.modelo,
        'fabricante': caminhao.fabricante, 'ano': caminhao.ano,
        'prefixo': caminhao.prefixo, 'chassi': caminhao.chassi
    })

@caminhao_bp.route('/api/caminhoes', methods=['POST'])
def cadastrar_caminhao():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    dados = request.get_json() or {}
    placa = dados.get('placa')
    modelo = dados.get('modelo')
    fabricante = dados.get('fabricante')
    ano = dados.get('ano')
    prefixo = dados.get('prefixo')
    chassi = dados.get('chassi')

    if not all([placa, modelo, fabricante, ano, prefixo, chassi]):
        return jsonify({'erro': 'Campos obrigatórios ausentes'}), 400

    if Caminhao.query.filter_by(placa=placa).first():
        return jsonify({'erro': 'Caminhão já cadastrado'}), 400

    novo_cam = Caminhao(
        placa=placa, modelo=modelo, fabricante=fabricante,
        ano=int(ano), prefixo=prefixo, chassi=chassi,
        usuario_id=session['usuario_id']
    )
    db.session.add(novo_cam)
    db.session.commit()
    return jsonify({'mensagem': 'Caminhão cadastrado com sucesso!'}), 201

@caminhao_bp.route('/api/caminhoes/<int:id>', methods=['DELETE'])
def excluir_caminhao(id):
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'erro': 'Caminhão não encontrado'}), 404

    db.session.delete(caminhao)
    db.session.commit()
    return jsonify({'mensagem': 'Caminhão excluído com sucesso!'}), 200

@caminhao_bp.route('/api/caminhoes/<int:id>', methods=['PUT'])
def editar_caminhao(id):
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'erro': 'Caminhão não encontrado'}), 404

    dados = request.get_json() or {}
    placa = dados.get('placa')
    modelo = dados.get('modelo')
    fabricante = dados.get('fabricante')
    ano = dados.get('ano')
    prefixo = dados.get('prefixo')
    chassi = dados.get('chassi')

    if not all([placa, modelo, fabricante, ano, prefixo, chassi]):
        return jsonify({'erro': 'Campos obrigatórios ausentes'}), 400

    # Verifica se a placa já existe em OUTRO caminhão
    placa_existente = Caminhao.query.filter(
        Caminhao.placa == placa, Caminhao.id != id
    ).first()
    if placa_existente:
        return jsonify({'erro': 'Já existe outro caminhão com essa placa'}), 400

    try:
        caminhao.placa = placa
        caminhao.modelo = modelo
        caminhao.fabricante = fabricante
        caminhao.ano = int(ano)
        caminhao.prefixo = prefixo
        caminhao.chassi = chassi
        db.session.commit()
        return jsonify({'mensagem': 'Caminhão atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao atualizar: {str(e)}'}), 500

@caminhao_bp.route('/api/caminhoes/<int:caminhao_id>/gastos', methods=['POST'])
def adicionar_gasto(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=caminhao_id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'error': 'Caminhão não encontrado'}), 404

    dados = request.get_json() or {}
    descricao = dados.get('descricao')
    valor = dados.get('valor')
    data_gasto = dados.get('data')
    tipo = dados.get('tipo', 'Manutenção') 
    quantidade = dados.get('quantidade')


    if not all([descricao, valor, data_gasto]):
        return jsonify({'error': 'Campos incompletos!'}), 400

    try:
        novo_gasto = Gasto(
            caminhao_id=caminhao_id,
            descricao=descricao,
            valor=float(valor),
            data=datetime.strptime(data_gasto, '%Y-%m-%d'),
            tipo=tipo,
            quantidade=quantidade
        )
        db.session.add(novo_gasto)
        db.session.commit()
        return jsonify({'message': 'Gasto adicionado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao salvar: {str(e)}'}), 500

@caminhao_bp.route('/api/caminhoes/<int:caminhao_id>/gastos', methods=['GET'])
def listar_gastos(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(
        id=caminhao_id,
        usuario_id=session['usuario_id']
    ).first()

    if not caminhao:
        return jsonify({'error': 'Caminhão não encontrado'}), 404

    gastos = Gasto.query.filter_by(caminhao_id=caminhao_id).all()

    resultado = []
    for g in gastos:
        resultado.append({
            'id': g.id,
            'descricao': g.descricao or '',
            'valor': float(g.valor or 0),
            'data': g.data.strftime('%Y-%m-%d') if g.data else '',
            'tipo': g.tipo or ''
        })

    return jsonify(resultado)

# ==================== ABASTECIMENTO ====================

@caminhao_bp.route('/api/caminhoes/<int:caminhao_id>/abastecimentos', methods=['POST'])
def adicionar_abastecimento(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=caminhao_id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'error': 'Caminhão não encontrado'}), 404

    dados = request.get_json() or {}
    litros = dados.get('litros')
    valor = dados.get('valor')
    data_abast = dados.get('data')
    km_atual = dados.get('km_atual')

    if not all([litros, valor, data_abast, km_atual]):
        return jsonify({'error': 'Campos incompletos!'}), 400

    try:
        novo = Abastecimento(
            caminhao_id=caminhao_id,
            litros=float(litros),
            valor=float(valor),
            data=datetime.strptime(data_abast, '%Y-%m-%d'),
            km_atual=float(km_atual)
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify({'message': 'Abastecimento registrado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao salvar: {str(e)}'}), 500

@caminhao_bp.route('/api/caminhoes/<int:caminhao_id>/abastecimentos', methods=['GET'])
def listar_abastecimentos(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    caminhao = Caminhao.query.filter_by(id=caminhao_id, usuario_id=session['usuario_id']).first()
    if not caminhao:
        return jsonify({'error': 'Caminhão não encontrado'}), 404

    abastecimentos = Abastecimento.query.filter_by(caminhao_id=caminhao_id).all()
    return jsonify([{
        'id': a.id,
        'litros': float(a.litros),
        'valor': float(a.valor),
        'data': a.data.strftime('%Y-%m-%d'),
        'km_atual': float(a.km_atual)
    } for a in abastecimentos])

@caminhao_bp.route('/api/abastecimentos/<int:id>', methods=['DELETE'])
@caminhao_bp.route('/api/gastos/abastecimento/<int:id>', methods=['DELETE'])
def excluir_abastecimento(id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    try:
        registro = Abastecimento.query.get(id)
        if not registro:
            return jsonify({"erro": "Abastecimento não encontrado."}), 404
        
        db.session.delete(registro)
        db.session.commit()
        return jsonify({"mensagem": "Abastecimento excluído com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao excluir abastecimento: {str(e)}"}), 500


@caminhao_bp.route('/api/gastos/item/<int:id>', methods=['DELETE'])
@caminhao_bp.route('/api/gastos/manutencao/<int:id>', methods=['DELETE'])
def excluir_gasto(id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    try:
        registro = Gasto.query.get(id)
        if not registro:
            return jsonify({"erro": "Gasto/Item não encontrado."}), 404
        
        db.session.delete(registro)
        db.session.commit()
        return jsonify({"mensagem": "Gasto excluído com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao excluir gasto: {str(e)}"}), 500


@caminhao_bp.route('/api/receitas/<int:id>', methods=['DELETE'])
@caminhao_bp.route('/api/gastos/receita/<int:id>', methods=['DELETE'])
def excluir_receita(id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    try:
        # Corrigido para buscar na tabela correta de Receita
        registro = Receita.query.get(id)
        if not registro:
            return jsonify({"erro": "Receita não encontrada."}), 404
            
        db.session.delete(registro)
        db.session.commit()
        return jsonify({"mensagem": "Receita excluída com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao excluir receita: {str(e)}"}), 500

# ==================== RECEITA ====================

@caminhao_bp.route('/api/caminhoes/<int:caminhao_id>/receitas', methods=['POST'])
def registrar_receita(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    dados = request.get_json()
    descricao = dados.get('descricao')
    valor = dados.get('valor')
    data_str = dados.get('data') # Recebe 'AAAA-MM-DD' do HTML5
    
    if not descricao or not valor or not data_str:
        return jsonify({'error': 'Preencha todos os campos obrigatórios'}), 400
        
    try:
        data_formatada = datetime.strptime(data_str, '%Y-%m-%d')
        
        nova_receita = Receita(
            caminhao_id=caminhao_id,
            descricao=descricao,
            valor=float(valor),
            data=data_formatada
        )
        db.session.add(nova_receita)
        db.session.commit()
        return jsonify({'message': 'Receita registrada com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@caminhao_bp.route('/api/caminhoes/<int:caminhao_id>/receitas', methods=['GET'])
def listar_receitas_backend(caminhao_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    try:
        receitas = Receita.query.filter_by(caminhao_id=caminhao_id).order_by(Receita.data.desc()).all()
        lista = []
        for r in receitas:
            lista.append({
                'id': r.id,
                'descricao': r.descricao,
                'valor': float(r.valor),
                'data': r.data.strftime('%Y-%m-%d') # Devolve formato ISO pro split do JS não quebrar
            })
        return jsonify(lista)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

