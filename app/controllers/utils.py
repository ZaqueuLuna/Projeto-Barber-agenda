from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def admin_obrigatorio(view):
    """Permite acesso só a usuários com perfil administrador."""
    @wraps(view)
    @login_required
    def envolvida(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return envolvida


def ler_data(texto, padrao=None):
    try:
        return date.fromisoformat(texto)
    except (TypeError, ValueError):
        return padrao


def ler_hora(texto):
    try:
        return time.fromisoformat(texto)
    except (TypeError, ValueError):
        return None


def ler_data_hora(data_txt, hora_txt):
    d, h = ler_data(data_txt), ler_hora(hora_txt)
    if d is None or h is None:
        return None
    return datetime.combine(d, h)


def ler_decimal(texto):
    try:
        return Decimal(str(texto).replace(",", "."))
    except (InvalidOperation, TypeError):
        return None


def ler_inteiro(texto):
    try:
        return int(texto)
    except (TypeError, ValueError):
        return None
