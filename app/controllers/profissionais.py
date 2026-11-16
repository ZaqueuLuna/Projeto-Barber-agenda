from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.controllers.utils import admin_obrigatorio, ler_hora
from app.models import Profissional

bp = Blueprint("profissionais", __name__, url_prefix="/profissionais")


@bp.route("/")
@admin_obrigatorio
def lista():
    profissionais = Profissional.query.order_by(Profissional.ativo.desc(), Profissional.nome).all()
    return render_template("profissionais/lista.html", profissionais=profissionais)


def _ler(form):
    nome = form.get("nome", "").strip()
    inicio, fim = ler_hora(form.get("hora_inicio")), ler_hora(form.get("hora_fim"))
    if not nome:
        return None, "Informe o nome do profissional."
    if inicio is None or fim is None or fim <= inicio:
        return None, "O horário de saída deve ser depois do horário de entrada."
    return {"nome": nome, "telefone": form.get("telefone", "").strip() or None,
            "hora_inicio": inicio, "hora_fim": fim}, None


@bp.route("/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo():
    valores = {"hora_inicio": "09:00", "hora_fim": "18:00"}
    if request.method == "POST":
        valores = request.form.to_dict()
        dados, erro = _ler(request.form)
        if dados:
            db.session.add(Profissional(**dados))
            db.session.commit()
            flash(f"Profissional {dados['nome']} cadastrado.", "sucesso")
            return redirect(url_for("profissionais.lista"))
        flash(erro, "erro")
    return render_template("profissionais/form.html", titulo="Novo profissional", valores=valores)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def editar(id):
    p = db.get_or_404(Profissional, id)
    valores = {"nome": p.nome, "telefone": p.telefone or "",
               "hora_inicio": p.hora_inicio.strftime("%H:%M"), "hora_fim": p.hora_fim.strftime("%H:%M")}
    if request.method == "POST":
        valores = request.form.to_dict()
        dados, erro = _ler(request.form)
        if dados:
            for campo, valor in dados.items():
                setattr(p, campo, valor)
            db.session.commit()
            flash("Alterações salvas.", "sucesso")
            return redirect(url_for("profissionais.lista"))
        flash(erro, "erro")
    return render_template("profissionais/form.html", titulo="Editar profissional",
                           valores=valores, profissional=p)


@bp.route("/<int:id>/ativo", methods=["POST"])
@admin_obrigatorio
def alternar_ativo(id):
    p = db.get_or_404(Profissional, id)
    p.ativo = not p.ativo
    db.session.commit()
    flash(f"Profissional {p.nome} {'reativado' if p.ativo else 'inativado'}.", "sucesso")
    return redirect(url_for("profissionais.lista"))
