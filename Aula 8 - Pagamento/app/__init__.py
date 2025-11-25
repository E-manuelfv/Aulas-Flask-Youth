from flask import Flask
import secrets

class MyFlaskApp:
    def __init__(self, config_object=None, **kwargs):
        # 1. Crie a instância do Flask e armazene-a
        self.app = Flask(__name__, template_folder='views/templates', static_folder='views/static', **kwargs)
        
        # 2. Agora use self.app.config para configurar
        self.app.config['SECRET_KEY'] = secrets.token_hex(16)
        
        if config_object:
            self.app.config.from_object(config_object)

        # 3. Registra Blueprints na instância 'self.app'
        from .controllers.auth import auth_bp
        from .controllers.shop import shop_bp 
        from .controllers.cart import cart_bp
        
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(shop_bp)
        self.app.register_blueprint(cart_bp, url_prefix='/cart')
    
    # Método para rodar a aplicação
    def run(self):
        self.app.run(debug=True)
        