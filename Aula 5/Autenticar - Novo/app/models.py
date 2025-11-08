from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

# Simulação de um banco de dados (por enquanto)
# A chave é o ID (como string), o valor é o objeto User
# IMPORTANTE: Os dados aqui são perdidos se o servidor reiniciar.
users_db = {}

class User(UserMixin):
    # O Flask-Login exige que o ID seja uma string
    def __init__(self, id, email, password):
        # Usamos UUID para IDs únicos em novos cadastros
        self.id = str(id) 
        self.email = email
        # NUNCA salve a senha em texto plano! Usamos hashing seguro
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash salvo."""
        return check_password_hash(self.password_hash, password)

    # --- Métodos estáticos para "simular" o DB ---
    
    @staticmethod
    def get(user_id):
        """Requerido pelo user_loader do Flask-Login para carregar o usuário."""
        # Usa o ID na sessão para buscar o objeto User
        return users_db.get(str(user_id))

    @staticmethod
    def get_by_email(email):
        """Método auxiliar para o login e checagem de cadastro."""
        for user in users_db.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def save(user):
        """Método auxiliar para salvar/atualizar o usuário no DB em memória."""
        users_db[str(user.id)] = user

# --- Criando um usuário de teste (SEED) ---
# Este usuário já existe quando a aplicação é iniciada.
u = User(id='1', email='aluno@exemplo.com', password='123')
User.save(u)

# O seu erro de registro ("email já cadastrado") acontece se você tentar cadastrar
# 'aluno@exemplo.com' ou se o servidor reiniciar e você tentar logar um usuário novo.
