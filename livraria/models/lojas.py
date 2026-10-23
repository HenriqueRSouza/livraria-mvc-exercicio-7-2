"""Model de lojas e estoque por unidade (R03)."""
from .banco import RegraInvalida, normalizar, registro


def debitar(db, edicao_id, loja_id):
    cursor = db.execute("UPDATE estoques SET quantidade=quantidade-1 WHERE edicao_id=? AND loja_id=? AND quantidade>0", (edicao_id, loja_id))
    if cursor.rowcount != 1:
        raise RegraInvalida("Sem estoque nesta unidade/edição.")


def creditar(db, edicao_id, loja_id):
    db.execute("UPDATE estoques SET quantidade=quantidade+1 WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id))


class Lojas:
    def __init__(self, banco):
        self.banco = banco

    def listar(self, bairro=""):
        with self.banco.conexao() as db:
            return [registro(r) for r in db.execute("SELECT * FROM lojas ORDER BY id") if normalizar(bairro) in normalizar(r["bairro"])]

    def estoque(self, edicao_id, loja_id):
        with self.banco.conexao() as db:
            item = registro(db.execute("SELECT * FROM estoques WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id)).fetchone())
            if not item:
                raise RegraInvalida("Edição ou loja inválida.")
            return item
