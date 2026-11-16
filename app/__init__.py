from decimal import Decimal

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Entre no sistema para acessar esta página."
login_manager.login_message_category = "aviso"

DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Usuario

    @login_manager.user_loader
    def carregar_usuario(user_id):
        return db.session.get(Usuario, int(user_id))

    from app.controllers import agenda, auth, clientes, painel, profissionais, servicos, usuarios
    for modulo in (auth, agenda, clientes, servicos, profissionais, painel, usuarios):
        app.register_blueprint(modulo.bp)

    @app.route("/")
    def inicio():
        return redirect(url_for("agenda.dia"))

    @app.template_filter("moeda")
    def moeda(valor):
        valor = Decimal(valor or 0)
        texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    @app.template_filter("data_extenso")
    def data_extenso(d):
        return f"{DIAS_SEMANA[d.weekday()]}, {d.day} de {MESES[d.month - 1]}"

    from app.comandos import registrar_comandos
    registrar_comandos(app)

    return app
