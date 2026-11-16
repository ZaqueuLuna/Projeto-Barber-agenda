from app import db


class Servico(db.Model):
    __tablename__ = "servico"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(8, 2), nullable=False)
    duracao_min = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
