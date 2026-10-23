from flask import Blueprint, render_template, request

from . import modelos

bp = Blueprint("lojas", __name__)


@bp.get("/lojas")
def listar():
    return render_template("lojas.html", lojas=modelos().lojas.listar(request.args.get("bairro", "")))
