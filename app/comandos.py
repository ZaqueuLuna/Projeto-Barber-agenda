"""Comandos de linha de comando: flask --app run criar-banco | popular."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import click

from app import db
from app.models import (STATUS_CONCLUIDO, Agendamento, Cliente, Profissional, Servico,
                        Usuario)
from app.models.usuario import PERFIL_ADMIN, PERFIL_RECEPCAO


def registrar_comandos(app):

    @app.cli.command("criar-banco")
    def criar_banco():
        """Cria as tabelas no banco configurado."""
        db.create_all()
        click.echo("Tabelas criadas.")

    @app.cli.command("popular")
    def popular():
        """Cria usuários de teste e dados de exemplo (só se o banco estiver vazio)."""
        db.create_all()
        if Usuario.query.first():
            click.echo("O banco já tem dados; nada foi alterado.")
            return

        admin = Usuario(nome="Administrador", email="admin", perfil=PERFIL_ADMIN)
        admin.definir_senha("admin")
        recepcao = Usuario(nome="Recepção", email="recepcao@barberagenda.com", perfil=PERFIL_RECEPCAO)
        recepcao.definir_senha("recepcao123")

        servicos = [Servico(nome="Corte", preco=Decimal("40.00"), duracao_min=30),
                    Servico(nome="Barba", preco=Decimal("30.00"), duracao_min=30),
                    Servico(nome="Corte e barba", preco=Decimal("65.00"), duracao_min=60),
                    Servico(nome="Sobrancelha", preco=Decimal("15.00"), duracao_min=15),
                    Servico(nome="Pigmentação", preco=Decimal("50.00"), duracao_min=45)]
        profissionais = [Profissional(nome="André", telefone="(81) 99999-0001",
                                      hora_inicio=time(9), hora_fim=time(18)),
                         Profissional(nome="Bruno", telefone="(81) 99999-0002",
                                      hora_inicio=time(9), hora_fim=time(18)),
                         Profissional(nome="Caio", telefone="(81) 99999-0003",
                                      hora_inicio=time(13), hora_fim=time(20))]
        clientes = [Cliente(nome=n, telefone=f"(81) 98888-00{i:02d}")
                    for i, n in enumerate(["Lucas Almeida", "Pedro Henrique", "Mateus Silva",
                                           "Rafael Costa", "João Victor", "Gabriel Souza"], 1)]
        db.session.add_all([admin, recepcao, *servicos, *profissionais, *clientes])
        db.session.flush()

        # Histórico de atendimentos
        hoje = date.today()
        historico = [(1, 0, 0, 9), (2, 1, 2, 10), (3, 0, 1, 11), (4, 2, 4, 14), (5, 1, 0, 15)]
        for dias_atras, prof, serv, hora in historico:
            inicio = datetime.combine(hoje - timedelta(days=dias_atras), time(hora))
            if profissionais[prof].hora_inicio.hour > hora:
                inicio = inicio.replace(hour=profissionais[prof].hora_inicio.hour)
            s = servicos[serv]
            db.session.add(Agendamento(
                cliente_id=clientes[(dias_atras + serv) % len(clientes)].id,
                profissional_id=profissionais[prof].id, servico_id=s.id, usuario_id=recepcao.id,
                inicio=inicio, fim=inicio + timedelta(minutes=s.duracao_min),
                preco_cobrado=s.preco, status=STATUS_CONCLUIDO))
        db.session.commit()
        click.echo("Dados de exemplo criados.")
        click.echo("Administrador: admin / admin")
        click.echo("Recepção:      recepcao@barberagenda.com / recepcao123")
