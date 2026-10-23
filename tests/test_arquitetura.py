"""Verifica a separação do MVC: o model não conhece a web e controllers/views não acessam o banco."""
import ast
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "livraria"


def importacoes(pasta):
    nomes = set()
    for arquivo in (RAIZ / pasta).rglob("*.py"):
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.Import):
                nomes.update(a.name.split(".")[0] for a in no.names)
            elif isinstance(no, ast.ImportFrom):
                nomes.add("." * no.level + (no.module or ""))
    return nomes


class ArquiteturaMVCTest(unittest.TestCase):
    def test_model_nao_depende_de_flask_nem_de_controllers_e_views(self):
        imports = importacoes("models")
        self.assertNotIn("flask", imports)
        self.assertFalse({i for i in imports if "controllers" in i or "views" in i})

    def test_controllers_nao_acessam_sqlite_diretamente(self):
        self.assertNotIn("sqlite3", importacoes("controllers"))

    def test_views_nao_acessam_model_nem_banco(self):
        imports = importacoes("views")
        self.assertNotIn("sqlite3", imports)
        self.assertFalse({i for i in imports if "models" in i})

    def test_cada_pagina_tem_template_proprio(self):
        templates = {p.name for p in (RAIZ / "views" / "templates").glob("*.html")}
        self.assertEqual(templates, {"base.html", "catalogo.html", "livro.html", "lojas.html", "entrada.html", "cliente.html"})


if __name__ == "__main__":
    unittest.main()
