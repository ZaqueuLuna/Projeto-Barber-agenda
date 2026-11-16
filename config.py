import os
import time

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

os.environ.setdefault("TZ", "America/Sao_Paulo")  # horário de Brasília
if hasattr(time, "tzset"):  # não existe no Windows
    time.tzset()

PRODUCAO = bool(os.environ.get("DATABASE_URL"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "barberagenda.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 280, "pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = PRODUCAO
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = PRODUCAO


if PRODUCAO and Config.SECRET_KEY == "chave-de-desenvolvimento":
    raise RuntimeError("Defina SECRET_KEY no arquivo .env antes de rodar em produção.")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
