from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.controllers.utils import admin_obrigatorio, ler_decimal, ler_inteiro
from app.models import Servico

bp = Blueprint("servicos", __name__, url_prefix="/servicos")


@bp.route("/")
@admin_obrigatorio
def lista():
    servicos = Servico.query.order_by(Servico.ativo.desc(), Servico.nome).all()
    return render_template("servicos/lista.html", servicos=servicos)


def _ler(form):
    nome = form.get("nome", "").strip()
    preco, duracao = ler_decimal(form.get("preco")), ler_inteiro(form.get("duracao_min"))
    if not nome:
        return None, "Informe o nome do serviço."
    if preco is None or preco < 0:
        return None, "Informe um preço válido, por exemplo 45,00."
    if duracao is None or not 5 <= duracao <= 480:
        return None, "A duração deve ficar entre 5 e 480 minutos."
    return {"nome": nome, "preco": preco, "duracao_min": duracao}, None


@bp.route("/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo():
    valores = {}
    if request.method == "POST":
        valores = request.form.to_dict()
        dados, erro = _ler(request.form)
        if dados:
            db.session.add(Servico(**dados))
            db.session.commit()
            flash(f"Serviço {dados['nome']} cadastrado.", "sucesso")
            return redirect(url_for("servicos.lista"))
        flash(erro, "erro")
    return render_template("servicos/form.html", titulo="Novo serviço", valores=valores)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def editar(id):
    s = db.get_or_404(Servico, id)
    valores = {"nome": s.nome, "preco": f"{s.preco:.2f}".replace(".", ","), "duracao_min": s.duracao_min}
    if request.method == "POST":
        valores = request.form.to_dict()
        dados, erro = _ler(request.form)
        if dados:
            for campo, valor in dados.items():
                setattr(s, campo, valor)
            db.session.commit()
            flash("Alterações salvas. Agendamentos já feitos mantêm o preço antigo.", "sucesso")
            return redirect(url_for("servicos.lista"))
        flash(erro, "erro")
    return render_template("servicos/form.html", titulo="Editar serviço", valores=valores, servico=s)


@bp.route("/<int:id>/ativo", methods=["POST"])
@admin_obrigatorio
def alternar_ativo(id):
    s = db.get_or_404(Servico, id)
    s.ativo = not s.ativo
    db.session.commit()
    flash(f"Serviço {s.nome} {'reativado' if s.ativo else 'inativado'}.", "sucesso")
    return redirect(url_for("servicos.lista"))
