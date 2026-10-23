from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from . import cliente_logado, logado, modelos

bp = Blueprint("clientes", __name__)


@bp.get("/cliente")
def area():
    cliente_id = cliente_logado()
    if not cliente_id:
        return render_template("entrada.html")
    m = modelos()
    return render_template("cliente.html", historico=m.pedidos.historico(cliente_id),
                           favoritos=m.clientes.favoritos(cliente_id), recomendacoes=m.clientes.recomendacoes(cliente_id),
                           notificacoes=m.clientes.notificacoes(cliente_id))


@bp.post("/cadastro")
def cadastro():
    session["cliente_id"] = modelos().clientes.cadastrar(
        request.form.get("nome", ""), request.form.get("email", ""),
        request.form.get("bairro", ""), request.form.get("interesses", ""))
    flash("Cadastro concluído. Esta é uma sessão local de demonstração.")
    return redirect(url_for("clientes.area"))


@bp.post("/entrar")
def entrar():
    session["cliente_id"] = modelos().clientes.por_email(request.form.get("email", ""))["id"]
    return redirect(url_for("clientes.area"))


@bp.post("/sair")
def sair():
    session.clear()
    return redirect(url_for("catalogo.index"))


@bp.post("/favorito/<int:livro_id>/<acao>")
@logado
def favorito(livro_id, acao):
    if acao not in ("adicionar", "remover"):
        abort(404)
    modelos().clientes.favorito(cliente_logado(), livro_id, acao == "adicionar")
    if acao == "adicionar":
        return redirect(url_for("catalogo.livro", livro_id=livro_id))
    return redirect(url_for("clientes.area"))
