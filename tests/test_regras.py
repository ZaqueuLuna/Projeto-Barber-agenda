"""Testes das regras de negócio (CT01 a CT08 do plano de testes)."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app import db
from app.models import STATUS_AGENDADO, ErroAgendamento, salvar_agendamento
from app.models.indicadores import faturamento
from tests.conftest import AGORA

DIA = AGORA.date()


def agendar(d, cliente, prof, serv, hora, minuto=0, **kw):
    inicio = datetime(DIA.year, DIA.month, DIA.day, hora, minuto)
    ag = salvar_agendamento(d[cliente], d[prof], d[serv], inicio, d["admin"], agora=AGORA, **kw)
    db.session.commit()
    return ag


def test_ct01_agendar_horario_livre(dados):
    ag = agendar(dados, "lucas", "andre", "corte", 10)
    assert ag.id is not None
    assert ag.status == STATUS_AGENDADO
    assert ag.fim - ag.inicio == timedelta(minutes=30)
    assert ag.preco_cobrado == Decimal("40.00")


def test_ct02_bloqueia_sobreposicao_mesmo_profissional(dados):
    agendar(dados, "lucas", "andre", "combo", 10)          # 10:00 às 11:00
    with pytest.raises(ErroAgendamento, match="Horário ocupado"):
        agendar(dados, "pedro", "andre", "corte", 10, 30)  # 10:30 às 11:00


def test_ct03_permite_mesmo_horario_outro_profissional(dados):
    agendar(dados, "lucas", "andre", "corte", 10)
    ag = agendar(dados, "pedro", "bruno", "corte", 10)
    assert ag.id is not None


def test_ct04_permite_logo_apos_o_fim(dados):
    agendar(dados, "lucas", "andre", "corte", 10)           # termina 10:30
    ag = agendar(dados, "pedro", "andre", "corte", 10, 30)  # começa 10:30
    assert ag.id is not None


def test_ct05_bloqueia_data_passada(dados):
    ontem = AGORA - timedelta(days=1)
    with pytest.raises(ErroAgendamento, match="já passou"):
        salvar_agendamento(dados["lucas"], dados["andre"], dados["corte"],
                           ontem.replace(hour=10), dados["admin"], agora=AGORA)


def test_ct06_bloqueia_fora_do_horario_do_profissional(dados):
    with pytest.raises(ErroAgendamento, match="atende das 09:00 às 18:00"):
        agendar(dados, "lucas", "andre", "combo", 17, 30)  # terminaria 18:30


def test_ct07_cancelar_libera_o_horario(dados):
    ag = agendar(dados, "lucas", "andre", "corte", 10)
    ag.cancelar("Cliente pediu para desmarcar")
    db.session.commit()
    novo = agendar(dados, "pedro", "andre", "corte", 10)
    assert novo.id is not None


def test_ct08_faturamento_soma_so_concluidos(dados):
    a = agendar(dados, "lucas", "andre", "corte", 10)   # 40
    b = agendar(dados, "pedro", "andre", "combo", 11)   # 65
    c = agendar(dados, "lucas", "bruno", "combo", 10)   # 65, será cancelado
    a.concluir()
    b.concluir()
    c.cancelar("Faltou")
    db.session.commit()
    inicio = datetime.combine(DIA, datetime.min.time())
    assert faturamento(inicio, inicio + timedelta(days=1)) == Decimal("105.00")


def test_remarcar_nao_conflita_consigo_mesmo(dados):
    ag = agendar(dados, "lucas", "andre", "combo", 10)  # 10:00 às 11:00
    remarcado = agendar(dados, "lucas", "andre", "combo", 10, 30, agendamento=ag)
    assert remarcado.id == ag.id
    assert remarcado.inicio.minute == 30


def test_cancelar_exige_motivo(dados):
    ag = agendar(dados, "lucas", "andre", "corte", 10)
    with pytest.raises(ErroAgendamento, match="motivo"):
        ag.cancelar("  ")


def test_preco_fica_congelado_apos_reajuste(dados):
    ag = agendar(dados, "lucas", "andre", "corte", 10)
    dados["corte"].preco = Decimal("50.00")
    db.session.commit()
    assert ag.preco_cobrado == Decimal("40.00")
