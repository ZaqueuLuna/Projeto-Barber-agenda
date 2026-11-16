from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import Usuario

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("agenda.dia"))

    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.ativo and usuario.verificar_senha(senha):
            login_user(usuario)
            destino = request.args.get("next")
            if (not destino or not destino.startswith("/")
                    or destino.startswith("//") or destino.startswith("/\\")):
                destino = url_for("agenda.dia")
            return redirect(destino)
        flash("Usuário ou senha incorretos. Confira os dados e tente de novo.", "erro")

    return render_template("login.html", email=email)


@bp.route("/senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    if request.method == "POST":
        atual = request.form.get("senha_atual", "")
        nova = request.form.get("nova_senha", "")
        confirmacao = request.form.get("confirmacao", "")
        if not current_user.verificar_senha(atual):
            flash("A senha atual está incorreta.", "erro")
        elif len(nova) < 6:
            flash("A nova senha precisa ter pelo menos 6 caracteres.", "erro")
        elif nova != confirmacao:
            flash("A confirmação não confere com a nova senha.", "erro")
        else:
            current_user.definir_senha(nova)
            db.session.commit()
            flash("Senha alterada.", "sucesso")
            return redirect(url_for("agenda.dia"))
    return render_template("senha.html")


@bp.route("/sair", methods=["POST"])
@login_required
def sair():
    logout_user()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("auth.login"))
