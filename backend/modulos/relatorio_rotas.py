from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from models import db, Caminhao, Gasto, Abastecimento 


relatorio_bp = Blueprint('relatorio_bp', __name__)


@relatorio_bp.route('/api/relatorio/gastos_detalhado', methods=['GET'])
def relatorio_gastos_detalhado():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    placa = request.args.get('placa')
    tipo = request.args.get('tipo')

    if not data_inicial or not data_final:
        return jsonify({'error': 'Datas são obrigatórias'}), 400

    try:
        d_ini = datetime.strptime(data_inicial, "%Y-%m-%d")
        d_fim = datetime.strptime(data_final, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Formato de data inválido.'}), 400

    usuario_id = session['usuario_id']

    # Query de gastos
    query = (
        db.session.query(Gasto, Caminhao)
        .join(Caminhao, Gasto.caminhao_id == Caminhao.id)
        .filter(Caminhao.usuario_id == usuario_id)
        .filter(Gasto.data >= d_ini)
        .filter(Gasto.data < d_fim)
    )

    if placa and placa != 'todos':
        query = query.filter(Caminhao.placa == placa)

  
    if tipo == 'Abastecimento':
       query = query.filter(Gasto.id == -1) 
    elif tipo and tipo != 'todos':
        query = query.filter(Gasto.tipo == tipo)

    gastos = query.order_by(Gasto.data.desc()).all()
    resultado = [{
        "placa": c.placa,
        "descricao": g.descricao,
        "tipo": g.tipo,
        "data": g.data.strftime("%Y-%m-%d"),
        "valor": float(g.valor)
    } for g, c in gastos]

    # Se tipo for Abastecimento ou todos, busca abastecimentos também
    if tipo in ('todos', 'Abastecimento'):
        query_abast = (
            db.session.query(Abastecimento, Caminhao)
            .join(Caminhao, Abastecimento.caminhao_id == Caminhao.id)
            .filter(Caminhao.usuario_id == usuario_id)
            .filter(Abastecimento.data >= d_ini)
            .filter(Abastecimento.data < d_fim)
        )
        if placa and placa != 'todos':
            query_abast = query_abast.filter(Caminhao.placa == placa)

        abastecimentos = query_abast.order_by(Abastecimento.data.desc()).all()
        for a, c in abastecimentos:
            resultado.append({
                "placa": c.placa,
                "descricao": f"Abastecimento — {float(a.litros)}L",
                "tipo": "Abastecimento",
                "data": a.data.strftime("%Y-%m-%d"),
                "valor": float(a.valor)
            })

    # Ordena tudo por data
    resultado.sort(key=lambda x: x['data'], reverse=True)
    return jsonify(resultado)