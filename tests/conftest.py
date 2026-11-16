from datetime import datetime, time
from decimal import Decimal

import pytest

from app import create_app, db
from app.models import Cliente, Profissional, Servico, Usuario
from config import TestConfig

AGORA = datetime(2030, 1, 7, 8, 0)  # data fixa no futuro para os testes


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def dados(app):
    admin = Usuario(nome="Admin", email="admin@teste.com", perfil="administrador")
    admin.definir_senha("segredo123")
    andre = Profissional(nome="André", hora_inicio=time(9), hora_fim=time(18))
    bruno = Profissional(nome="Bruno", hora_inicio=time(9), hora_fim=time(18))
    corte = Servico(nome="Corte", preco=Decimal("40.00"), duracao_min=30)
    combo = Servico(nome="Corte e barba", preco=Decimal("65.00"), duracao_min=60)
    lucas = Cliente(nome="Lucas", telefone="1")
    pedro = Cliente(nome="Pedro", telefone="2")
    db.session.add_all([admin, andre, bruno, corte, combo, lucas, pedro])
    db.session.commit()
    return {"admin": admin, "andre": andre, "bruno": bruno, "corte": corte,
            "combo": combo, "lucas": lucas, "pedro": pedro}


@pytest.fixture
def cliente_http(app):
    return app.test_client()
