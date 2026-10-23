# Tarefas derivadas de livraria.md

Marcar somente após verificar a tarefa. IDs de aceitação referem-se à especificação.

- [x] T01 Estruturar projeto, especificação e tarefas (C01–C08); conferir arquivos e commit.
- [x] T02 Escrever testes do domínio antes do código; registrar falha inicial (C01–C07). Falha: `ModuleNotFoundError: No module named 'livraria'`.
- [x] T03 Criar banco e dados de demonstração idempotentes; validar persistência e estoque por loja (C02,C03).
- [x] T04 Implementar busca, detalhes, preços, lojas e comparações; passar testes (C01–C03).
- [x] T05 Implementar clientes, favoritos, recomendações e promoções; passar testes (C04,C07).
- [x] T06 Implementar reserva, cancelamento, retirada, compra direta e pontos; passar testes (C05,C06).
- [x] T07 Implementar alertas e reposição simulada; passar testes (C07).
- [x] T08 Construir rotas Flask e interface navegável; verificar fluxos HTTP (C08). Testes HTTP e servidor HTTP 200.
- [x] T09 Documentar execução e limitações, testar tudo e percorrer fluxos; verificar commits (C01–C08). 10 testes passaram; servidor Flask respondeu HTTP 200.

## Exercício 7 — arquitetura

- [x] T10 Desenhar arquitetura do aplicativo (contexto, containers, módulos, fluxo de reserva, decisões) em `docs/arquitetura.md` (exercício 7.1).
- [x] T11 Separar regras e SQL em models por módulo sem dependência de Flask; C01–C07 passam nos models (exercício 7.2).
- [x] T12 Separar rotas em controllers (blueprints) e o template único em views por página; C08 passa via HTTP.
- [x] T13 Documentar a arquitetura MVC no README com diagrama.
