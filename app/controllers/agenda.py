from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.controllers.utils import ler_data, ler_data_hora, ler_inteiro
from app.models import (STATUS_CANCELADO, Agendamento, Cliente, ErroAgendamento,
                        Profissional, Servico, salvar_agendamento)

bp = Blueprint("agenda", __name__, url_prefix="/agenda")

PX_POR_MINUTO = 1.2  # 72 px por hora na grade


def _opcoes_formulario():
    return {
        "clientes": Cliente.query.filter_by(ativo=True).order_by(Cliente.nome).all(),
        "profissionais": Profissional.query.filter_by(ativo=True).order_by(Profissional.nome).all(),
        "servicos": Servico.query.filter_by(ativo=True).order_by(Servico.nome).all(),
    }


@bp.route("/")
@login_required
def dia():
    dia = ler_data(request.args.get("data"), date.today())
    profissionais = Profissional.query.filter_by(ativo=True).order_by(Profissional.nome).all()

    abre = min((p.hora_inicio for p in profissionais), default=time(8))
    fecha = max((p.hora_fim for p in profissionais), default=time(19))
    h0, h1 = abre.hour, fecha.hour + (1 if fecha.minute else 0)
    base = datetime.combine(dia, time(h0))

    agendamentos = Agendamento.query.filter(
        Agendamento.inicio >= datetime.combine(dia, time.min),
        Agendamento.inicio < datetime.combine(dia + timedelta(days=1), time.min),
        Agendamento.status != STATUS_CANCELADO,
    ).order_by(Agendamento.inicio).all()

    colunas = {p.id: [] for p in profissionais}
    for ag in agendamentos:
        if ag.profissional_id in colunas:
            minutos = (ag.inicio - base).total_seconds() / 60
            duracao = (ag.fim - ag.inicio).total_seconds() / 60
            colunas[ag.profissional_id].append({
                "ag": ag,
                "topo": round(minutos * PX_POR_MINUTO),
                "altura": max(round(duracao * PX_POR_MINUTO) - 3, 22),
            })

    horas = [(f"{h:02d}:00", round((h - h0) * 60 * PX_POR_MINUTO)) for h in range(h0, h1)]

    return render_template(
        "agenda/dia.html", dia=dia, hoje=date.today(),
        anterior=dia - timedelta(days=1), proximo=dia + timedelta(days=1),
        profissionais=profissionais, colunas=colunas, horas=horas,
        altura=round((h1 - h0) * 60 * PX_POR_MINUTO), total=len(agendamentos),
    )


def _salvar_do_formulario(agendamento=None):
    """Retorna (agendamento, erro)."""
    cliente = db.session.get(Cliente, ler_inteiro(request.form.get("cliente_id")) or 0)
    profissional = db.session.get(Profissional, ler_inteiro(request.form.get("profissional_id")) or 0)
    servico = db.session.get(Servico, ler_inteiro(request.form.get("servico_id")) or 0)
    inicio = ler_data_hora(request.form.get("data"), request.form.get("hora"))
    if inicio is None:
        return None, "Informe a data e a hora do atendimento."
    try:
        ag = salvar_agendamento(cliente, profissional, servico, inicio, current_user,
                                agendamento=agendamento)
        db.session.commit()
        return ag, None
    except ErroAgendamento as erro:
        db.session.rollback()
        return None, str(erro)


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    valores = {
        "data": request.args.get("data", date.today().isoformat()),
        "hora": request.args.get("hora", ""),
        "profissional_id": request.args.get("profissional_id", ""),
        "cliente_id": request.args.get("cliente_id", ""),
        "servico_id": "",
    }
    if request.method == "POST":
        valores = request.form.to_dict()
        ag, erro = _salvar_do_formulario()
        if ag:
            flash(f"Agendamento criado: {ag.cliente.nome} às {ag.inicio:%H:%M} com {ag.profissional.nome}.", "sucesso")
            return redirect(url_for("agenda.dia", data=ag.inicio.date().isoformat()))
        flash(erro, "erro")
    return render_template("agenda/form.html", titulo="Novo agendamento",
                           valores=valores, botao="Agendar", **_opcoes_formulario())


@bp.route("/<int:id>")
@login_required
def detalhe(id):
    ag = db.get_or_404(Agendamento, id)
    return render_template("agenda/detalhe.html", ag=ag)


@bp.route("/<int:id>/remarcar", methods=["GET", "POST"])
@login_required
def remarcar(id):
    ag = db.get_or_404(Agendamento, id)
    valores = {
        "cliente_id": str(ag.cliente_id), "profissional_id": str(ag.profissional_id),
        "servico_id": str(ag.servico_id), "data": ag.inicio.date().isoformat(),
        "hora": ag.inicio.strftime("%H:%M"),
    }
    if request.method == "POST":
        valores = request.form.to_dict()
        salvo, erro = _salvar_do_formulario(agendamento=ag)
        if salvo:
            flash(f"Agendamento remarcado para {salvo.inicio:%d/%m às %H:%M}.", "sucesso")
            return redirect(url_for("agenda.dia", data=salvo.inicio.date().isoformat()))
        flash(erro, "erro")
    return render_template("agenda/form.html", titulo="Remarcar agendamento", ag=ag,
                           valores=valores, botao="Remarcar", **_opcoes_formulario())


@bp.route("/<int:id>/concluir", methods=["POST"])
@login_required
def concluir(id):
    ag = db.get_or_404(Agendamento, id)
    try:
        ag.concluir()
        db.session.commit()
        flash(f"Atendimento de {ag.cliente.nome} concluído.", "sucesso")
    except ErroAgendamento as erro:
        flash(str(erro), "erro")
    return redirect(url_for("agenda.dia", data=ag.inicio.date().isoformat()))


@bp.route("/<int:id>/cancelar", methods=["POST"])
@login_required
def cancelar(id):
    ag = db.get_or_404(Agendamento, id)
    try:
        ag.cancelar(request.form.get("motivo", ""))
        db.session.commit()
        flash(f"Agendamento de {ag.cliente.nome} cancelado. O horário está livre.", "sucesso")
        return redirect(url_for("agenda.dia", data=ag.inicio.date().isoformat()))
    except ErroAgendamento as erro:
        flash(str(erro), "erro")
        return redirect(url_for("agenda.detalhe", id=id))
