from flask import Flask
from flask_login import LoginManager

# 1. Instanciamos o LoginManager FORA da classe
login_manager = LoginManager()
# 2. Definimos a rota de login (nome do blueprint.nome da função).
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info' 

class MyApp:
    def __init__(self):
        # Configura caminhos relativos
        self.app = Flask(__name__, template_folder='views/templates', static_folder='views/static')
        
        # 3. CONFIGURAÇÃO DA SESSÃO: Isso é OBRIGATÓRIO!
        self.app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-dificil-de-adivinhar'
        
        # 4. Vincula o LoginManager à nossa instância 'app'
        login_manager.init_app(self.app)
        
        # 5. Registra o 'user_loader'
        self.register_user_loader()
        
        # 6. Registra os Blueprints
        self.register_blueprints()

    def register_user_loader(self):
        """ Ensina o Flask-Login a carregar um usuário a partir do ID na sessão. """
        # Importa o modelo localmente para evitar problemas de dependência circular
        from .models import User 
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.get(user_id) # Usa nosso método estático

    def register_blueprints(self):
        """ Importa e registra os módulos da aplicação. """
        # Importamos as rotas AQUI
        from .auth.routes import bp as auth_bp
        from .main.routes import bp as main_bp
        
        # Registra os Blueprints
        self.app.register_blueprint(auth_bp, url_prefix='/auth')
        self.app.register_blueprint(main_bp, url_prefix='/')

    def run(self):
        self.app.run(debug=True)
