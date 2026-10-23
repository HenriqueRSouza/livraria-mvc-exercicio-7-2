"""Model do catálogo: livros, edições, avaliações e preço promocional (R01, R02)."""
from .banco import RegraInvalida, normalizar, registro


def preco_final(db, edicao_id):
    row = db.execute("SELECT preco_centavos FROM edicoes WHERE id=?", (edicao_id,)).fetchone()
    if not row:
        raise RegraInvalida("Edição inválida.")
    desconto = db.execute("SELECT COALESCE(SUM(desconto_centavos),0) FROM promocoes WHERE edicao_id=? AND ativa=1", (edicao_id,)).fetchone()[0]
    return max(0, row[0] - desconto)


class Catalogo:
    def __init__(self, banco):
        self.banco = banco

    def buscar_livros(self, titulo="", autor="", genero=""):
        with self.banco.conexao() as db:
            livros = [registro(r) for r in db.execute("SELECT * FROM livros ORDER BY id")]
        return [b for b in livros if all(normalizar(termo) in normalizar(b[campo])
                for campo, termo in (("titulo", titulo), ("autor", autor), ("genero", genero)) if termo)]

    def detalhes_livro(self, livro_id):
        with self.banco.conexao() as db:
            livro = registro(db.execute("SELECT * FROM livros WHERE id=?", (livro_id,)).fetchone())
            if not livro:
                raise RegraInvalida("Livro não encontrado.")
            livro["avaliacoes"] = [registro(r) for r in db.execute("SELECT * FROM avaliacoes WHERE livro_id=? ORDER BY id", (livro_id,))]
            livro["edicoes"] = []
            for row in db.execute("SELECT * FROM edicoes WHERE livro_id=? ORDER BY id", (livro_id,)).fetchall():
                ed = registro(row)
                ed["promocoes"] = [registro(r) for r in db.execute("SELECT * FROM promocoes WHERE edicao_id=? AND ativa=1", (ed["id"],))]
                ed["preco_final_centavos"] = max(0, ed["preco_centavos"] - sum(p["desconto_centavos"] for p in ed["promocoes"]))
                ed["estoques"] = [registro(r) for r in db.execute("SELECT e.*, l.nome AS loja_nome FROM estoques e JOIN lojas l ON l.id=e.loja_id WHERE e.edicao_id=? ORDER BY e.loja_id", (ed["id"],))]
                livro["edicoes"].append(ed)
            return livro
