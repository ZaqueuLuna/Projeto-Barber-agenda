from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app import db
from app.controllers.utils import admin_obrigatorio
from app.models import Usuario
from app.models.usuario import PERFIL_ADMIN, PERFIL_RECEPCAO

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@bp.route("/")
@admin_obrigatorio
def lista():
    usuarios = Usuario.query.order_by(Usuario.ativo.desc(), Usuario.nome).all()
    return render_template("usuarios/lista.html", usuarios=usuarios)


@bp.route("/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo():
    valores = {"perfil": PERFIL_RECEPCAO}
    if request.method == "POST":
        valores = request.form.to_dict()
        nome = valores.get("nome", "").strip()
        email = valores.get("email", "").strip().lower()
        senha = valores.get("senha", "")
        perfil = valores.get("perfil")
        erro = None
        if not nome or not email:
            erro = "Preencha o nome e o e-mail."
        elif len(senha) < 6:
            erro = "A senha precisa ter pelo menos 6 caracteres."
        elif perfil not in (PERFIL_ADMIN, PERFIL_RECEPCAO):
            erro = "Escolha um perfil."
        elif Usuario.query.filter_by(email=email).first():
            erro = "Já existe um usuário com esse e-mail."
        if not erro:
            u = Usuario(nome=nome, email=email, perfil=perfil)
            u.definir_senha(senha)
            db.session.add(u)
            db.session.commit()
            flash(f"Usuário {nome} criado.", "sucesso")
            return redirect(url_for("usuarios.lista"))
        flash(erro, "erro")
    return render_template("usuarios/form.html", valores=valores)


@bp.route("/<int:id>/ativo", methods=["POST"])
@admin_obrigatorio
def alternar_ativo(id):
    u = db.get_or_404(Usuario, id)
    if u.id == current_user.id:
        flash("Você não pode inativar o próprio usuário.", "erro")
    else:
        u.ativo = not u.ativo
        db.session.commit()
        flash(f"Usuário {u.nome} {'reativado' if u.ativo else 'inativado'}.", "sucesso")
    return redirect(url_for("usuarios.lista"))
