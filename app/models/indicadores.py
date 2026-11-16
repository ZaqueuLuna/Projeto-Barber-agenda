"""Consultas do painel. RN05: só agendamentos concluídos entram no faturamento."""
from datetime import datetime, timedelta

from sqlalchemy import func

from app import db
from app.models.agendamento import STATUS_AGENDADO, STATUS_CONCLUIDO, Agendamento
from app.models.servico import Servico


def _periodo_dia(dia):
    inicio = datetime.combine(dia, datetime.min.time())
    return inicio, inicio + timedelta(days=1)


def _periodo_mes(dia):
    inicio = datetime(dia.year, dia.month, 1)
    fim = datetime(dia.year + (dia.month == 12), dia.month % 12 + 1, 1)
    return inicio, fim


def faturamento(inicio, fim):
    total = db.session.query(func.coalesce(func.sum(Agendamento.preco_cobrado), 0)).filter(
        Agendamento.status == STATUS_CONCLUIDO,
        Agendamento.inicio >= inicio, Agendamento.inicio < fim,
    ).scalar()
    return total


def contar(status, inicio, fim):
    return Agendamento.query.filter(
        Agendamento.status == status,
        Agendamento.inicio >= inicio, Agendamento.inicio < fim,
    ).count()


def servicos_mais_vendidos(inicio, fim, limite=5):
    return (db.session.query(Servico.nome, func.count(Agendamento.id).label("qtd"))
            .join(Agendamento, Agendamento.servico_id == Servico.id)
            .filter(Agendamento.status == STATUS_CONCLUIDO,
                    Agendamento.inicio >= inicio, Agendamento.inicio < fim)
            .group_by(Servico.nome)
            .order_by(func.count(Agendamento.id).desc(), Servico.nome)
            .limit(limite).all())


def resumo(dia):
    d0, d1 = _periodo_dia(dia)
    m0, m1 = _periodo_mes(dia)
    return {
        "concluidos_dia": contar(STATUS_CONCLUIDO, d0, d1),
        "abertos_dia": contar(STATUS_AGENDADO, d0, d1),
        "faturamento_dia": faturamento(d0, d1),
        "concluidos_mes": contar(STATUS_CONCLUIDO, m0, m1),
        "faturamento_mes": faturamento(m0, m1),
        "top_servicos": servicos_mais_vendidos(m0, m1),
    }
