"""Model de pedidos: reserva, cancelamento, retirada, compra direta e fidelidade (R05)."""
from .banco import RegraInvalida, registro
from .catalogo import preco_final
from .clientes import cliente_valido
from .lojas import creditar, debitar


class Pedidos:
    def __init__(self, banco):
        self.banco = banco

    def reservar(self, cliente_id, edicao_id, loja_id):
        with self.banco.conexao() as db:
            db.execute("BEGIN IMMEDIATE")
            cliente_valido(db, cliente_id)
            preco = preco_final(db, edicao_id)
            debitar(db, edicao_id, loja_id)
            identificador = db.execute("INSERT INTO reservas(cliente_id,edicao_id,loja_id,estado,preco_centavos) VALUES (?,?,?,'confirmada',?)", (cliente_id, edicao_id, loja_id, preco)).lastrowid
            codigo = f"RES-{identificador:06d}"
            db.execute("UPDATE reservas SET codigo=? WHERE id=?", (codigo, identificador))
            return registro(db.execute("SELECT * FROM reservas WHERE id=?", (identificador,)).fetchone())

    def _reserva_confirmada(self, db, cliente_id, codigo):
        cliente_valido(db, cliente_id)
        row = db.execute("SELECT * FROM reservas WHERE codigo=? AND cliente_id=? AND estado='confirmada'", (codigo, cliente_id)).fetchone()
        if not row:
            raise RegraInvalida("Reserva inexistente, de outro cliente ou já finalizada.")
        return row

    def cancelar(self, cliente_id, codigo):
        with self.banco.conexao() as db:
            db.execute("BEGIN IMMEDIATE")
            reserva = self._reserva_confirmada(db, cliente_id, codigo)
            db.execute("UPDATE reservas SET estado='cancelada' WHERE id=?", (reserva["id"],))
            creditar(db, reserva["edicao_id"], reserva["loja_id"])

    def retirar(self, cliente_id, codigo):
        with self.banco.conexao() as db:
            db.execute("BEGIN IMMEDIATE")
            reserva = self._reserva_confirmada(db, cliente_id, codigo)
            db.execute("UPDATE reservas SET estado='retirada' WHERE id=?", (reserva["id"],))
            identificador = db.execute("INSERT INTO compras(cliente_id,edicao_id,loja_id,preco_centavos,reserva_id) VALUES (?,?,?,?,?)", (cliente_id, reserva["edicao_id"], reserva["loja_id"], reserva["preco_centavos"], reserva["id"])).lastrowid
            return registro(db.execute("SELECT * FROM compras WHERE id=?", (identificador,)).fetchone())

    def comprar(self, cliente_id, edicao_id, loja_id):
        with self.banco.conexao() as db:
            db.execute("BEGIN IMMEDIATE")
            cliente_valido(db, cliente_id)
            preco = preco_final(db, edicao_id)
            debitar(db, edicao_id, loja_id)
            identificador = db.execute("INSERT INTO compras(cliente_id,edicao_id,loja_id,preco_centavos) VALUES (?,?,?,?)", (cliente_id, edicao_id, loja_id, preco)).lastrowid
            return registro(db.execute("SELECT * FROM compras WHERE id=?", (identificador,)).fetchone())

    def historico(self, cliente_id):
        with self.banco.conexao() as db:
            cliente_valido(db, cliente_id)
            reservas = [registro(r) for r in db.execute("SELECT r.*, b.titulo, e.nome AS edicao, l.nome AS loja, s.secao FROM reservas r JOIN edicoes e ON e.id=r.edicao_id JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=r.loja_id JOIN estoques s ON s.edicao_id=r.edicao_id AND s.loja_id=r.loja_id WHERE r.cliente_id=? ORDER BY r.id DESC", (cliente_id,))]
            compras = [registro(r) for r in db.execute("SELECT c.*, b.titulo, e.nome AS edicao, l.nome AS loja FROM compras c JOIN edicoes e ON e.id=c.edicao_id JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=c.loja_id WHERE c.cliente_id=? ORDER BY c.id DESC", (cliente_id,))]
            return {"reservas": reservas, "compras": compras, "pontos": sum(c["preco_centavos"] // 100 for c in compras)}
