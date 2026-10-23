from flask import Blueprint, abort, flash, redirect, request, url_for

from . import cliente_logado, logado, modelos

bp = Blueprint("pedidos", __name__)


@bp.post("/reservar")
@logado
def reservar():
    reserva = modelos().pedidos.reservar(cliente_logado(), int(request.form["edicao_id"]), int(request.form["loja_id"]))
    flash(f"Reserva confirmada: {reserva['codigo']}. Retire na unidade selecionada; pagamento simulado apenas na retirada.")
    return redirect(url_for("clientes.area"))


@bp.post("/comprar")
@logado
def comprar():
    compra = modelos().pedidos.comprar(cliente_logado(), int(request.form["edicao_id"]), int(request.form["loja_id"]))
    flash(f"Compra presencial simulada registrada: #{compra['id']} (sem cobrança real).")
    return redirect(url_for("clientes.area"))


@bp.post("/reserva/<codigo>/<acao>")
@logado
def reserva_acao(codigo, acao):
    if acao == "retirar":
        modelos().pedidos.retirar(cliente_logado(), codigo)
        flash(f"Retirada de {codigo} concluída; compra simulada registrada.")
    elif acao == "cancelar":
        modelos().pedidos.cancelar(cliente_logado(), codigo)
        flash(f"Reserva {codigo} cancelada; estoque devolvido.")
    else:
        abort(404)
    return redirect(url_for("clientes.area"))
