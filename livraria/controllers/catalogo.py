from flask import Blueprint, render_template, request

from . import modelos

bp = Blueprint("catalogo", __name__)


@bp.get("/")
def index():
    livros = modelos().catalogo.buscar_livros(
        request.args.get("titulo", ""), request.args.get("autor", ""), request.args.get("genero", ""))
    return render_template("catalogo.html", livros=livros)


@bp.get("/livro/<int:livro_id>")
def livro(livro_id):
    return render_template("livro.html", livro=modelos().catalogo.detalhes_livro(livro_id))
