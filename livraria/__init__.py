"""Livraria em MVC: models (regras + SQLite), views (templates) e controllers (blueprints Flask)."""
import os

from flask import Flask, flash, redirect, request, session, url_for

from . import views
from .controllers import catalogo, clientes, comunicacao, lojas, pedidos
from .models import Modelos, RegraInvalida


def create_app(db_path=None):
    app = Flask(__name__, template_folder=str(views.TEMPLATES))
    app.secret_key = os.environ.get("LIVRARIA_SECRET", "chave-local-apenas-demonstracao")
    modelos = Modelos(db_path or os.environ.get("LIVRARIA_DB", "livraria.db"))
    app.extensions["modelos"] = modelos
    views.registrar(app)

    for modulo in (catalogo, lojas, clientes, pedidos, comunicacao):
        app.register_blueprint(modulo.bp)

    @app.errorhandler(RegraInvalida)
    def erro(exc):
        flash(str(exc), "erro")
        return redirect(request.referrer or url_for("catalogo.index"))

    @app.context_processor
    def contexto():
        cliente_id = session.get("cliente_id")
        return {"cliente_atual": modelos.clientes.obter(cliente_id) if cliente_id else None}

    return app
