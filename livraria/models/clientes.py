"""Model de clientes: cadastro, favoritos, recomendações e notificações (R02, R04)."""
import re
import sqlite3

from .banco import RegraInvalida, normalizar, registro


def cliente_valido(db, cliente_id):
    cliente = db.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone()
    if not cliente:
        raise RegraInvalida("Cliente inválido; cadastre-se primeiro.")
    return cliente


class Clientes:
    def __init__(self, banco):
        self.banco = banco

    def cadastrar(self, nome, email, bairro, interesses=""):
        nome, email, bairro = nome.strip(), email.strip().lower(), bairro.strip()
        if not nome or not bairro or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise RegraInvalida("Informe nome, email válido e bairro.")
        interesses = ",".join(p.strip() for p in interesses.split(",") if p.strip())
        with self.banco.conexao() as db:
            try:
                cliente = db.execute("INSERT INTO clientes(nome,email,bairro,interesses) VALUES (?,?,?,?)", (nome, email, bairro, interesses)).lastrowid
            except sqlite3.IntegrityError as exc:
                raise RegraInvalida("Email já cadastrado.") from exc
            for p in db.execute("SELECT p.descricao, b.genero FROM promocoes p JOIN edicoes e ON e.id=p.edicao_id JOIN livros b ON b.id=e.livro_id WHERE p.ativa=1"):
                if normalizar(p["genero"]) in [normalizar(x) for x in interesses.split(",")]:
                    db.execute("INSERT INTO notificacoes(cliente_id,tipo,mensagem) VALUES (?,'promocao',?)", (cliente, p["descricao"]))
            return cliente

    def por_email(self, email):
        with self.banco.conexao() as db:
            row = db.execute("SELECT * FROM clientes WHERE email=? COLLATE NOCASE", (email.strip(),)).fetchone()
            if not row:
                raise RegraInvalida("Email não cadastrado.")
            return registro(row)

    def obter(self, cliente_id):
        with self.banco.conexao() as db:
            return registro(cliente_valido(db, cliente_id))

    def favorito(self, cliente_id, livro_id, adicionar=True):
        with self.banco.conexao() as db:
            cliente_valido(db, cliente_id)
            if not db.execute("SELECT 1 FROM livros WHERE id=?", (livro_id,)).fetchone():
                raise RegraInvalida("Livro inválido.")
            if adicionar:
                db.execute("INSERT OR IGNORE INTO favoritos VALUES (?,?)", (cliente_id, livro_id))
            else:
                db.execute("DELETE FROM favoritos WHERE cliente_id=? AND livro_id=?", (cliente_id, livro_id))

    def favoritos(self, cliente_id):
        with self.banco.conexao() as db:
            cliente_valido(db, cliente_id)
            return [registro(r) for r in db.execute("SELECT b.* FROM livros b JOIN favoritos f ON b.id=f.livro_id WHERE f.cliente_id=? ORDER BY b.id", (cliente_id,))]

    def recomendacoes(self, cliente_id):
        with self.banco.conexao() as db:
            cliente = cliente_valido(db, cliente_id)
            interesses = [normalizar(x.strip()) for x in cliente["interesses"].split(",") if x.strip()]
            return [registro(r) for r in db.execute("SELECT * FROM livros b WHERE NOT EXISTS (SELECT 1 FROM favoritos f WHERE f.livro_id=b.id AND f.cliente_id=?) ORDER BY id", (cliente_id,)) if normalizar(r["genero"]) in interesses]

    def notificacoes(self, cliente_id):
        with self.banco.conexao() as db:
            cliente_valido(db, cliente_id)
            return [registro(r) for r in db.execute("SELECT * FROM notificacoes WHERE cliente_id=? ORDER BY id DESC", (cliente_id,))]
