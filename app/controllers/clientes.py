from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app import db
from app.models import Cliente

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.route("/")
@login_required
def lista():
    busca = request.args.get("q", "").strip()
    consulta = Cliente.query
    if busca:
        termo = f"%{busca}%"
        consulta = consulta.filter(or_(Cliente.nome.ilike(termo), Cliente.telefone.ilike(termo)))
    clientes = consulta.order_by(Cliente.ativo.desc(), Cliente.nome).all()
    return render_template("clientes/lista.html", clientes=clientes, busca=busca)


def _validar(form):
    nome, telefone = form.get("nome", "").strip(), form.get("telefone", "").strip()
    if not nome or not telefone:
        return "Preencha o nome e o telefone do cliente."
    return None


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    valores = {}
    if request.method == "POST":
        valores = request.form.to_dict()
        erro = _validar(request.form)
        if not erro:
            c = Cliente(nome=valores["nome"].strip(), telefone=valores["telefone"].strip(),
                        email=valores.get("email", "").strip() or None)
            db.session.add(c)
            db.session.commit()
            flash(f"Cliente {c.nome} cadastrado.", "sucesso")
            if request.args.get("voltar") == "agenda":
                return redirect(url_for("agenda.novo", cliente_id=c.id))
            return redirect(url_for("clientes.lista"))
        flash(erro, "erro")
    return render_template("clientes/form.html", titulo="Novo cliente", valores=valores)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    c = db.get_or_404(Cliente, id)
    valores = {"nome": c.nome, "telefone": c.telefone, "email": c.email or ""}
    if request.method == "POST":
        valores = request.form.to_dict()
        erro = _validar(request.form)
        if not erro:
            c.nome, c.telefone = valores["nome"].strip(), valores["telefone"].strip()
            c.email = valores.get("email", "").strip() or None
            db.session.commit()
            flash("Alterações salvas.", "sucesso")
            return redirect(url_for("clientes.lista"))
        flash(erro, "erro")
    return render_template("clientes/form.html", titulo="Editar cliente", valores=valores, cliente=c)


@bp.route("/<int:id>/ativo", methods=["POST"])
@login_required
def alternar_ativo(id):
    c = db.get_or_404(Cliente, id)
    c.ativo = not c.ativo  # RN06: inativa, nunca exclui
    db.session.commit()
    flash(f"Cliente {c.nome} {'reativado' if c.ativo else 'inativado'}.", "sucesso")
    return redirect(url_for("clientes.lista"))
