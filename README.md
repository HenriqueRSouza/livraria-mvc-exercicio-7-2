# Livraria — Exercícios 7.1 e 7.2 (Arquitetura de Software)

Continuação da livraria do [exercício 6](https://github.com/HenriqueRSouza/livraria-sdd-exercicio-6).

- **7.1 Design de arquitetura:** [docs/arquitetura.md](docs/arquitetura.md)
- **7.2 Arquitetura MVC:** o código deste repositório

## 7.2 — MVC

O MVP foi refatorado para o padrão Model-View-Controller e continua com front-end funcional.


```
livraria/
├── controllers/   # Controller: rotas Flask (catalogo, lojas, clientes, pedidos, comunicacao)
├── models/        # Model: regras de negócio + acesso ao banco SQLite
└── views/
    └── templates/ # View: páginas HTML (base, catalogo, livro, lojas, entrada, cliente)
app.py             # inicia o servidor
tests/             # testes dos models e das rotas
```

| Parte | O que faz |
|---|---|
| **Model** | estrutura dos dados e acesso ao banco. Ex.: `models/pedidos.py` reserva, cancela e calcula os pontos |
| **View** | interface gráfica. Cada página é um template que herda de `base.html` |
| **Controller** | recebe a requisição, chama o model e escolhe a view. Ex.: `controllers/pedidos.py` |

**O que mudou em relação ao exercício 6:** antes havia um `livraria.py` com todas as regras, um `app.py` com todas as rotas e um único `index.html`. Agora cada responsabilidade ficou na sua pasta.

## Como rodar

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Abra http://127.0.0.1:5000/. O banco `livraria.db` é criado sozinho com livros e lojas de exemplo.

## Testes

```sh
.venv/bin/python -m unittest discover -v
```
