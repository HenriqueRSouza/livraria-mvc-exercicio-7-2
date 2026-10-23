"""Model de comunicação: alertas de reposição e reposição simulada (R06)."""
from .banco import RegraInvalida
from .clientes import cliente_valido
from .lojas import creditar


class Comunicacao:
    def __init__(self, banco):
        self.banco = banco

    def alertar(self, cliente_id, edicao_id, loja_id):
        with self.banco.conexao() as db:
            cliente_valido(db, cliente_id)
            item = db.execute("SELECT quantidade FROM estoques WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id)).fetchone()
            if not item or item[0] != 0:
                raise RegraInvalida("Alerta permitido apenas para edição esgotada na unidade.")
            db.execute("INSERT OR IGNORE INTO alertas VALUES (?,?,?)", (cliente_id, edicao_id, loja_id))

    def repor(self, edicao_id, loja_id):
        with self.banco.conexao() as db:
            db.execute("BEGIN IMMEDIATE")
            item = db.execute("SELECT b.titulo, l.nome FROM estoques s JOIN edicoes e ON e.id=s.edicao_id JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=s.loja_id WHERE s.edicao_id=? AND s.loja_id=?", (edicao_id, loja_id)).fetchone()
            if not item:
                raise RegraInvalida("Edição ou loja inválida.")
            creditar(db, edicao_id, loja_id)
            db.execute("INSERT INTO notificacoes(cliente_id,tipo,mensagem) SELECT cliente_id,'reposicao',? FROM alertas WHERE edicao_id=? AND loja_id=?", (f"Reposição simulada: {item[0]} em {item[1]}", edicao_id, loja_id))
            db.execute("DELETE FROM alertas WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id))
