from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

PERFIL_ADMIN = "administrador"
PERFIL_RECEPCAO = "recepcionista"


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.Enum(PERFIL_ADMIN, PERFIL_RECEPCAO, name="perfil_usuario"),
                       nullable=False, default=PERFIL_RECEPCAO)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self):
        return self.perfil == PERFIL_ADMIN

    @property
    def is_active(self):
        return self.ativo
