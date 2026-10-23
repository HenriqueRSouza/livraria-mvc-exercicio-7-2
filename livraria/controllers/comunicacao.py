from flask import Blueprint, flash, redirect, request, url_for

from . import cliente_logado, logado, modelos

bp = Blueprint("comunicacao", __name__)


@bp.post("/alertar")
@logado
def alertar():
    modelos().comunicacao.alertar(cliente_logado(), int(request.form["edicao_id"]), int(request.form["loja_id"]))
    flash("Alerta local registrado; consulte sua área após simular reposição.")
    return redirect(request.referrer or url_for("catalogo.index"))


@bp.post("/repor")
def repor():
    modelos().comunicacao.repor(int(request.form["edicao_id"]), int(request.form["loja_id"]))
    flash("Reposição simulada: uma unidade adicionada e notificações locais geradas.")
    return redirect(request.referrer or url_for("catalogo.index"))
