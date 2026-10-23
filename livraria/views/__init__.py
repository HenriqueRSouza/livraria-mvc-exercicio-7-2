"""View do MVC: templates Jinja e formatação de apresentação."""
from pathlib import Path

TEMPLATES = Path(__file__).parent / "templates"


def reais(centavos):
    return f"R$ {centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def registrar(app):
    app.add_template_filter(reais, "reais")
