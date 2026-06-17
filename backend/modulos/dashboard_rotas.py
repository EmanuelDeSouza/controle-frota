from flask import Blueprint, jsonify, session
from sqlalchemy import func
from models import db, Gasto, Abastecimento, Caminhao, Receita

dashboard_bp = Blueprint('dashboard_bp', __name__)

def calcular_consumo_medio_veiculo(caminhao_id):
    """
    Calcula o consumo médio (km/L) de um veículo com base no histórico de abastecimentos.
    Aplica a lógica: (Km_atual - Km_anterior) / Litros_atual para trechos consecutivos.
    """
    # Busca os abastecimentos associados ao caminhao_id ordenados por KM crescente
    abastecimentos = Abastecimento.query.filter_by(caminhao_id=caminhao_id)\
                                        .order_by(Abastecimento.km.asc())\
                                        .all()
    
    # Caso de borda 1: Mínimo de 2 abastecimentos necessários
    if len(abastecimentos) < 2:
        return "Sem dados suficientes"
    
    total_distancia = 0
    total_litros = 0
    trechos_validos = 0
    
    # Percorre os abastecimentos calculando a diferença entre trechos consecutivos
    for i in range(1, len(abastecimentos)):
        abastecimento_anterior = abastecimentos[i - 1]
        abastecimento_atual = abastecimentos[i]
        
        distancia_trecho = abastecimento_atual.km - abastecimento_anterior.km
        litros_trecho = abastecimento_atual.litros
        
        # Caso de borda 2: Proteção contra KM decrescente ou erro de digitação de litros
        if distancia_trecho <= 0 or litros_trecho <= 0:
            continue  
            
        total_distancia += distancia_trecho
        total_litros += litros_trecho
        trechos_validos += 1
        
    # Se após filtrar os erros de digitação nenhum trecho restou válido
    if trechos_validos == 0 or total_litros == 0:
        return "Sem dados suficientes"
        
    # Média ponderada real do consumo
    consumo_medio = total_distancia / total_litros
    
    return f"{consumo_medio:.2f} km/L"


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def dados_dashboard():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
        
    usuario_id = session['usuario_id']
    
    try:
        # ==================== 1. ACUMULADO GERAL DOS CARDS ====================
        res_gastos = db.session.query(func.sum(Gasto.valor))\
            .join(Caminhao, Gasto.caminhao_id == Caminhao.id)\
            .filter(Caminhao.usuario_id == usuario_id).scalar()
        gastos_gerais = float(res_gastos) if res_gastos is not None else 0.0

        res_abast = db.session.query(func.sum(Abastecimento.valor))\
            .join(Caminhao, Abastecimento.caminhao_id == Caminhao.id)\
            .filter(Caminhao.usuario_id == usuario_id).scalar()
        abastecimentos_total = float(res_abast) if res_abast is not None else 0.0

        total_despesas_unificadas = gastos_gerais + abastecimentos_total

        res_receitas = db.session.query(func.sum(Receita.valor))\
            .join(Caminhao, Receita.caminhao_id == Caminhao.id)\
            .filter(Caminhao.usuario_id == usuario_id).scalar()
        total_receitas = float(res_receitas) if res_receitas is not None else 0.0
        
        lucro_liquido = total_receitas - total_despesas_unificadas

        # ==================== 2. GRÁFICO (Todas as Categorias Dinâmicas) ====================
        query_categorias = db.session.query(Gasto.tipo, func.sum(Gasto.valor))\
            .join(Caminhao, Gasto.caminhao_id == Caminhao.id)\
            .filter(Caminhao.usuario_id == usuario_id)\
            .group_by(Gasto.tipo).all()
            
        gastos_mapeados = {}
        for tipo, valor in query_categorias:
            if tipo:
                nome_tipo = str(tipo).strip().capitalize()
                gastos_mapeados[nome_tipo] = gastos_mapeados.get(nome_tipo, 0.0) + float(valor)
        
        # Insere a categoria de Abastecimento se houver dados
        if abastecimentos_total > 0:
            gastos_mapeados["Abastecimento"] = gastos_mapeados.get("Abastecimento", 0.0) + abastecimentos_total

        gastos_por_categoria = [{"tipo": k, "valor": v} for k, v in gastos_mapeados.items()]

        # ==================== 3. TABELA (Resumo por Caminhão) ====================
        caminhoes = Caminhao.query.filter_by(usuario_id=usuario_id).all()
        resumo_caminhoes = []

        for caminhao in caminhoes:
            val_g = db.session.query(func.sum(Gasto.valor)).filter(Gasto.caminhao_id == caminhao.id).scalar()
            g_individual = float(val_g) if val_g is not None else 0.0
            
            val_a = db.session.query(func.sum(Abastecimento.valor)).filter(Abastecimento.caminhao_id == caminhao.id).scalar()
            a_individual = float(val_a) if val_a is not None else 0.0
            
            val_r = db.session.query(func.sum(Receita.valor)).filter(Receita.caminhao_id == caminhao.id).scalar()
            r_individual = float(val_r) if val_r is not None else 0.0
            
            gastos_totais_caminhao = g_individual + a_individual
            lucro_caminhao = r_individual - gastos_totais_caminhao
            
            # Executa a regra matemática do consumo médio para o caminhão atual
            consumo_veiculo = calcular_consumo_medio_veiculo(caminhao.id)
            
            resumo_caminhoes.append({
                "placa": caminhao.placa,
                "modelo": caminhao.modelo if hasattr(caminhao, 'modelo') else "Não Informado",
                "total_gastos": gastos_totais_caminhao,
                "total_receitas": r_individual,
                "lucro": lucro_caminhao,
                "consumo_medio": consumo_veiculo  # Chave injetada com sucesso no JSON
            })

        return jsonify({
            "total_gastos": total_despesas_unificadas,
            "total_abastecimento": abastecimentos_total,
            "total_receitas": total_receitas,
            "lucro": lucro_liquido,
            "gastos_por_categoria": gastos_por_categoria,
            "resumo_caminhoes": resumo_caminhoes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500