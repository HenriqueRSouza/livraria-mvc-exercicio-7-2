"""Ponto de entrada local da livraria (MVC)."""
from livraria import create_app

if __name__ == "__main__":
    create_app().run(debug=False)
