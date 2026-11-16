"""Testes de acesso e telas (CT09 e CT10)."""
from datetime import date, timedelta

import pytest


def entrar(cliente, email="admin@teste.com", senha="segredo123"):
    return cliente.post("/login", data={"email": email, "senha": senha}, follow_redirects=True)


def test_ct09_pagina_protegida_redireciona_para_login(cliente_http):
    resposta = cliente_http.get("/agenda/")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_ct10_senha_errada_nega_acesso(cliente_http, dados):
    resposta = entrar(cliente_http, senha="errada")
    assert "Usuário ou senha incorretos" in resposta.get_data(as_text=True)


@pytest.mark.parametrize("url", ["/agenda/", "/agenda/novo", "/clientes/", "/clientes/novo",
                                 "/servicos/", "/servicos/novo", "/profissionais/",
                                 "/profissionais/novo", "/painel/", "/usuarios/", "/usuarios/novo"])
def test_paginas_abrem_para_o_administrador(cliente_http, dados, url):
    entrar(cliente_http)
    assert cliente_http.get(url).status_code == 200


def test_recepcionista_nao_acessa_area_do_administrador(cliente_http, dados):
    from app import db
    from app.models import Usuario
    r = Usuario(nome="Recepção", email="rec@teste.com", perfil="recepcionista")
    r.definir_senha("segredo123")
    db.session.add(r)
    db.session.commit()
    entrar(cliente_http, "rec@teste.com")
    assert cliente_http.get("/painel/").status_code == 403
    assert cliente_http.get("/clientes/").status_code == 200


def test_fluxo_completo_pela_interface(cliente_http, dados):
    entrar(cliente_http)
    amanha = (date.today() + timedelta(days=1)).isoformat()
    form = {"cliente_id": dados["lucas"].id, "profissional_id": dados["andre"].id,
            "servico_id": dados["corte"].id, "data": amanha, "hora": "10:00"}
    r = cliente_http.post("/agenda/novo", data=form, follow_redirects=True)
    assert "Agendamento criado" in r.get_data(as_text=True)

    form["cliente_id"] = dados["pedro"].id
    r = cliente_http.post("/agenda/novo", data=form, follow_redirects=True)
    assert "Horário ocupado" in r.get_data(as_text=True)

    r = cliente_http.get(f"/agenda/?data={amanha}")
    assert "Lucas" in r.get_data(as_text=True)

    r = cliente_http.post("/agenda/1/concluir", follow_redirects=True)
    assert "concluído" in r.get_data(as_text=True)
    assert cliente_http.get("/agenda/1").status_code == 200


def test_usuario_altera_a_propria_senha(cliente_http, dados):
    entrar(cliente_http)
    r = cliente_http.post("/senha", data={"senha_atual": "errada", "nova_senha": "nova12345",
                                          "confirmacao": "nova12345"}, follow_redirects=True)
    assert "senha atual está incorreta" in r.get_data(as_text=True)

    r = cliente_http.post("/senha", data={"senha_atual": "segredo123", "nova_senha": "nova12345",
                                          "confirmacao": "nova12345"}, follow_redirects=True)
    assert "Senha alterada" in r.get_data(as_text=True)

    cliente_http.post("/sair")
    assert "incorretos" in entrar(cliente_http).get_data(as_text=True)
    assert "incorretos" not in entrar(cliente_http, senha="nova12345").get_data(as_text=True)


@pytest.mark.parametrize("destino", ["//exemplo.com", "/\\exemplo.com", "https://exemplo.com"])
def test_login_nao_redireciona_para_outro_site(cliente_http, dados, destino):
    resposta = cliente_http.post(f"/login?next={destino}",
                                 data={"email": "admin@teste.com", "senha": "segredo123"})
    assert resposta.headers["Location"] == "/agenda/"
