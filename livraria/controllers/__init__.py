"""Controllers do MVC: recebem a ação do usuário, chamam o model e escolhem a view."""
from functools import wraps

from flask import current_app, flash, redirect, session, url_for


def modelos():
    return current_app.extensions["modelos"]


def cliente_logado():
    return session.get("cliente_id")


def logado(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not cliente_logado():
            flash("Cadastre-se ou entre para continuar.", "erro")
            return redirect(url_for("clientes.area"))
        return fn(*args, **kwargs)
    return wrapper
