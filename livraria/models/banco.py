"""Acesso ao SQLite compartilhado pelos models, com esquema e dados de demonstração."""
import sqlite3
import unicodedata
from contextlib import contextmanager


class RegraInvalida(ValueError):
    """Operação não permitida pela especificação."""


def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)).casefold()
                   if not unicodedata.combining(c))


def registro(row):
    return dict(row) if row else None


class Banco:
    def __init__(self, caminho):
        self.caminho = str(caminho)

    @contextmanager
    def conexao(self):
        db = sqlite3.connect(self.caminho, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def init_db(self):
        with self.conexao() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS livros(id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, autor TEXT NOT NULL, genero TEXT NOT NULL, sinopse TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS edicoes(id INTEGER PRIMARY KEY, livro_id INTEGER NOT NULL REFERENCES livros, nome TEXT NOT NULL, ano INTEGER NOT NULL, preco_centavos INTEGER NOT NULL CHECK(preco_centavos>=0));
                CREATE TABLE IF NOT EXISTS lojas(id INTEGER PRIMARY KEY, nome TEXT NOT NULL, bairro TEXT NOT NULL, endereco TEXT NOT NULL, horario TEXT NOT NULL, pagamentos TEXT NOT NULL, servicos TEXT NOT NULL, cafe INTEGER NOT NULL, eventos TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS estoques(edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, quantidade INTEGER NOT NULL CHECK(quantidade>=0), secao TEXT NOT NULL, PRIMARY KEY(edicao_id,loja_id));
                CREATE TABLE IF NOT EXISTS avaliacoes(id INTEGER PRIMARY KEY, livro_id INTEGER NOT NULL REFERENCES livros, nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5), texto TEXT NOT NULL, autor TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS promocoes(id INTEGER PRIMARY KEY, edicao_id INTEGER NOT NULL REFERENCES edicoes, descricao TEXT NOT NULL, desconto_centavos INTEGER NOT NULL CHECK(desconto_centavos>=0), ativa INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, bairro TEXT NOT NULL, interesses TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS favoritos(cliente_id INTEGER NOT NULL REFERENCES clientes, livro_id INTEGER NOT NULL REFERENCES livros, PRIMARY KEY(cliente_id,livro_id));
                CREATE TABLE IF NOT EXISTS reservas(id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes, edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, codigo TEXT UNIQUE, estado TEXT NOT NULL CHECK(estado IN ('confirmada','retirada','cancelada')), preco_centavos INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS compras(id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes, edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, preco_centavos INTEGER NOT NULL, reserva_id INTEGER UNIQUE REFERENCES reservas);
                CREATE TABLE IF NOT EXISTS alertas(cliente_id INTEGER NOT NULL REFERENCES clientes, edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, PRIMARY KEY(cliente_id,edicao_id,loja_id));
                CREATE TABLE IF NOT EXISTS notificacoes(id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes, tipo TEXT NOT NULL, mensagem TEXT NOT NULL);
            """)
            if db.execute("SELECT 1 FROM livros LIMIT 1").fetchone():
                return
            db.executemany("INSERT INTO livros VALUES (?,?,?,?,?)", [
                (1, "A Casa das Marés", "L. Andrade", "Ficção", "Uma viagem às memórias de uma cidade costeira."),
                (2, "Python para Todos", "Ana Ribeiro", "Tecnologia", "Introdução prática à programação."),
            ])
            db.executemany("INSERT INTO edicoes VALUES (?,?,?,?,?)", [
                (1, 1, "Brochura", 2024, 5000), (2, 1, "Capa dura", 2025, 7500),
                (3, 2, "Brochura", 2024, 8000),
            ])
            db.executemany("INSERT INTO lojas VALUES (?,?,?,?,?,?,?,?,?)", [
                (1, "Unidade Centro", "Centro", "Rua das Flores, 10", "Seg–Sáb 9h–18h", "Pix, cartão (simulados)", "Retirada, acessibilidade", 1, "Clube do livro aos sábados"),
                (2, "Unidade Jardim", "Jardim", "Av. Verde, 22", "Seg–Sáb 10h–19h", "Pix, cartão (simulados)", "Retirada", 0, "Oficina de leitura mensal"),
            ])
            db.executemany("INSERT INTO estoques VALUES (?,?,?,?)", [
                (1, 1, 1, "Literatura"), (1, 2, 2, "Ficção"), (2, 1, 0, "Literatura"),
                (2, 2, 1, "Ficção"), (3, 1, 2, "Tecnologia"), (3, 2, 0, "Tecnologia"),
            ])
            db.execute("INSERT INTO avaliacoes VALUES (1,1,5,'Envolvente','Leitora demo')")
            db.execute("INSERT INTO promocoes VALUES (1,1,'Oferta de demonstração',1000,1)")
