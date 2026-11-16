from datetime import date

from flask import Blueprint, render_template

from app.controllers.utils import admin_obrigatorio
from app.models.indicadores import resumo

bp = Blueprint("painel", __name__, url_prefix="/painel")


@bp.route("/")
@admin_obrigatorio
def inicio():
    hoje = date.today()
    dados = resumo(hoje)
    maior = max((qtd for _, qtd in dados["top_servicos"]), default=0)
    return render_template("painel.html", hoje=hoje, maior=maior, **dados)
