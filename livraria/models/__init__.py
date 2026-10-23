"""Model do MVC: regras de negócio e dados da livraria, sem dependência de Flask."""
from .banco import Banco, RegraInvalida
from .catalogo import Catalogo
from .clientes import Clientes
from .comunicacao import Comunicacao
from .lojas import Lojas
from .pedidos import Pedidos


class Modelos:
    """Reúne os models sobre um mesmo banco; é o que os controllers recebem."""

    def __init__(self, caminho):
        self.banco = Banco(caminho)
        self.banco.init_db()
        self.catalogo = Catalogo(self.banco)
        self.lojas = Lojas(self.banco)
        self.clientes = Clientes(self.banco)
        self.pedidos = Pedidos(self.banco)
        self.comunicacao = Comunicacao(self.banco)


__all__ = ["Modelos", "RegraInvalida"]
