# Exercício 7.1 — Design de arquitetura do aplicativo da livraria

Este documento desenha a arquitetura de software do aplicativo da livraria especificado em [specs/livraria.md](specs/livraria.md). Ele serve de referência para as implementações dos exercícios 7.2 (MVC), 7.3 (multicamadas) e 7.4 (Clean).

## 1. Contexto

Quem usa o sistema e com o que ele conversa.

```mermaid
flowchart LR
    cliente([Cliente<br/>navegador web/celular])
    funcionario([Funcionário da loja<br/>balcão / reposição])
    subgraph sistema[Aplicativo da Livraria]
        app[Aplicação web]
    end
    pagamento[[Gateway de pagamento<br/>simulado]]
    mensagens[[Email / push / SMS<br/>simulado]]

    cliente -- "busca, reserva, compra, favoritos" --> app
    funcionario -- "retirada com código, reposição" --> app
    app -. "cobrança (fora do escopo da demo)" .-> pagamento
    app -. "avisos (hoje só notificações locais)" .-> mensagens
```

Integrações externas aparecem tracejadas: na demonstração elas são simuladas localmente (sem cobrança real nem envio de mensagens), mas a arquitetura reserva o ponto de extensão para elas.

## 2. Containers

```mermaid
flowchart TB
    browser[Navegador<br/>HTML + formulários]
    subgraph servidor[Servidor Python]
        web[Front-end web<br/>Flask + Jinja2<br/>rotas, sessão, templates]
        nucleo[Núcleo da livraria<br/>regras de negócio]
        persist[Persistência<br/>repositórios]
    end
    db[(Armazenamento<br/>SQLite ou arquivo TXT)]

    browser -- HTTP --> web
    web --> nucleo
    nucleo --> persist
    persist --> db
```

| Container | Responsabilidade | Tecnologia |
|---|---|---|
| Front-end web | Renderizar páginas, ler formulários, manter sessão do cliente, mostrar mensagens | Flask 3, Jinja2 |
| Núcleo | Regras R01–R06: busca, preço promocional, reserva/retirada/cancelamento, pontos, alertas | Python puro |
| Persistência | Ler/gravar entidades com transações atômicas (estoque não pode ficar negativo) | SQLite (7.2, 7.3) / TXT (7.4) |

## 3. Módulos do núcleo

```mermaid
flowchart LR
    catalogo[Catálogo<br/>livros, edições,<br/>avaliações, promoções]
    lojas[Lojas e estoque<br/>unidades, seções,<br/>quantidade por loja]
    clientes[Clientes<br/>cadastro, favoritos,<br/>recomendações]
    pedidos[Pedidos<br/>reservas, compras,<br/>fidelidade]
    comunicacao[Comunicação<br/>alertas de reposição,<br/>notificações]

    pedidos --> catalogo
    pedidos --> lojas
    pedidos --> clientes
    comunicacao --> lojas
    comunicacao --> clientes
    clientes --> catalogo
```

Cada módulo é dono das suas tabelas/registros. Pedidos consultam o preço no catálogo e debitam estoque em lojas dentro da mesma transação, o que garante R05 (último exemplar não é vendido duas vezes).

## 4. Fluxo principal: reservar e retirar

```mermaid
sequenceDiagram
    actor C as Cliente
    participant W as Front-end web
    participant P as Pedidos
    participant E as Lojas/Estoque
    participant D as Armazenamento
    C->>W: POST /reservar (edição, loja)
    W->>P: reservar(cliente, edição, loja)
    P->>D: inicia transação
    P->>E: debitar 1 unidade (se quantidade > 0)
    P->>D: grava reserva "confirmada" + código RES-000001
    P->>D: commit
    P-->>W: reserva
    W-->>C: código, loja, seção, preço
    C->>W: POST /reserva/RES-000001/retirar
    W->>P: retirar(cliente, código)
    P->>D: reserva → "retirada" + compra (sem novo débito)
    W-->>C: histórico e pontos atualizados
```

## 5. Decisões de arquitetura

| Decisão | Motivo |
|---|---|
| Monólito modular em vez de microsserviços | Uma equipe, um banco pequeno e transações que cruzam estoque e pedidos; dividir em serviços agora traria rede e consistência eventual sem benefício. Os módulos da seção 3 são as fronteiras naturais se um dia forem separados. |
| Renderização no servidor (Jinja) | Front-end funcional sem build de JavaScript; formulários HTML cobrem todas as ações. |
| Núcleo sem dependência de Flask | Permite testar regras sem HTTP e trocar a interface. É o ponto que 7.2 → 7.3 → 7.4 vai reforçando. |
| Valores em centavos inteiros | Evita erro de arredondamento em preço, desconto e pontos. |
| Integrações externas simuladas | Escopo de demonstração; ficam atrás de uma fronteira para serem trocadas por serviços reais. |

## 6. Como cada exercício materializa este desenho

| Exercício | Estilo | Onde o desenho aparece |
|---|---|---|
| 7.2 | MVC | Models = núcleo + persistência por módulo; Views = templates Jinja; Controllers = blueprints Flask por módulo |
| 7.3 | Multicamadas (4 camadas) | Apresentação → Aplicação → Domínio e Dados (Dados só conhece as entidades do Domínio); nova feature: avaliações de clientes |
| 7.4 | Clean Architecture | Entidades ← Casos de uso (portas) ← Adaptadores (TXT) ← Frameworks (Flask); DIP isola o núcleo da tecnologia de armazenamento |
