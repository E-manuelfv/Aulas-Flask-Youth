### Ponto de Partida: O Problema do `MyApp`

Na aula anterior, terminamos com uma classe `MyApp` que continha toda a lógica da aplicação:

```python
# Código antigo
class MyApp:
    def __init__(self):
        self.app = Flask(...)
        self.app.add_url_rule('/login', 'login', self.login)
        self.app.add_url_rule('/', 'index', self.index)
    
    def login(self): ...
    def index(self): ...
```

**Problema:** À medida que adicionamos "logout", "registro", "perfil", "posts" (e tudo do mini-projeto), o `__init__` e a própria classe `MyApp` se tornarão gigantes e difíceis de manter.

**Solução:** Vamos usar o conceito da [**Aula 4.5](https://www.notion.so/Aula-4-5-Flask-Blueprints-29139ef840d780318026c297ecdb815d?pvs=21) (Blueprints)** para refatorar. A classe `MyApp` se tornará uma "Fábrica de Aplicação" (Application Factory) que *inicializa* e *registra* os módulos (Blueprints), em vez de conter a lógica das rotas diretamente.

---

### Nova Estrutura de Projeto (MVC + [Blueprints](https://www.notion.so/Aula-4-5-Flask-Blueprints-29139ef840d780318026c297ecdb815d?pvs=21))

Vamos reorganizar nosso projeto para refletir essa modularidade:

```
projeto_flask/
├── app/
│   ├── __init__.py      # Onde ficará nossa classe MyApp (agora uma "fábrica")
│   ├── auth/            # Blueprint de Autenticação
│   │   ├── __init__.py  # Define o Blueprint 'auth'
│   │   └── routes.py    # Rotas (views) de login, logout, register
│   ├── main/            # Blueprint Principal (rotas públicas, index)
│   │   ├── __init__.py  # Define o Blueprint 'main'
│   │   └── routes.py    # Rota index, e futuramente a área restrita (perfil)
│   ├── models.py        # O "M" do MVC: Nosso modelo User
│   └── views/           # Nossos templates e estáticos
│       ├── templates/
│       │   ├── auth/    # Templates específicos da autenticação
│       │   │   └── login.html
│       │   └── index.html
│       └── static/
└── run.py               # Arquivo principal para executar a aplicação
```