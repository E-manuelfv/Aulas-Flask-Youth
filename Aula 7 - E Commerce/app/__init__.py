from flask import Flask
import secrets

class MyFlaskApp:
    def __init__(self, config_object=None, **kwargs):
        self.app = Flask(__name__, template_folder='views/templates', static_folder='views/static', **kwargs)
        
        self.app.config['SECRET_KEY'] = secrets.token_hex(16)
        
        if config_object:
            self.app.config.from_object(config_object)

        # Registra Blueprints na instância 'self.app'
        from .controllers.auth import auth_bp
        from .controllers.main import main_bp 
        from .controllers.cart import cart_bp
        
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(cart_bp)
    
    # Método para rodar a aplicação
    def run(self):
        self.app.run(debug=True)
        