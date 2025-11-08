from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# Importa o cliente Supabase configurado
from app.models.supabase_client import supabase 

from functools import wraps

# ----------------------------------------------------
# DECORADOR CUSTOMIZADO PARA SUPABASE (Não usa Flask-Login)
# ----------------------------------------------------
def login_required(f):
    """
    Verifica se o 'user_id' está na sessão do Flask,
    indicando que o usuário se autenticou via Supabase.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Usamos 'user_id' que foi armazenado na sessão durante o login
        if 'user_id' not in session:
            # Se não estiver logado, exibe uma mensagem e redireciona para o login.
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            
            # Redireciona para o login e anexa a URL atual
            # (?next=/profile) para que o Flask possa redirecionar de volta após o login.
            return redirect(url_for('auth.login', next=request.url))
        
        # Se o user_id existir na sessão, a função original (f) é executada.
        return f(*args, **kwargs)
    return decorated_function

auth_bp = Blueprint('auth', __name__, url_prefix='/auth',template_folder='../../views/templates/auth')

# --- Rota de Registro ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'] 
        password = request.form['password']
        
        if not supabase:
            flash('Erro de configuração do Supabase.', 'danger')
            return redirect(url_for('auth.register'))

        try:
            # 1. Chama a função de registro do Supabase
            res = supabase.auth.sign_up({"email": email, "password": password})
            
            # Nota: O Supabase por padrão envia um e-mail de confirmação.
            # O usuário só estará autenticado após confirmar o e-mail (depende das suas configurações no Supabase).
            
            flash('Registro completo! Verifique seu Email.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            # Captura erros como: e-mail já registrado, senha fraca, etc.
            flash(f'Registration failed: {e}', 'danger')
            return render_template('register.html', email=email)
    
    # Renderiza o template de registro (Certifique-se de que o form tenha um campo 'email' e 'password')
    return render_template('auth/register.html') # Ajustei o caminho do template para seguir sua estrutura

# --- Rota de Login ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not supabase:
            flash('Erro de configuração do Supabase.', 'danger')
            return redirect(url_for('auth.login'))
        
        try:
            # 2. Chama a função de login do Supabase
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            # Se o login for bem-sucedido, armazena as informações essenciais na sessão do Flask
            # Isso é crucial para manter o estado de login
            session['user_id'] = res.user.id
            session['user_email'] = res.user.email
            session['access_token'] = res.session.access_token # Token para interagir com o PostgREST
            
            flash('Login successful!', 'success')
            # Você precisará ter uma rota 'home' registrada em outro Blueprint ou no __init__.py
            return redirect(url_for('shop.index')) # Exemplo redirecionando para a loja
            
        except Exception as e:
            # Captura erros como: credenciais inválidas, e-mail não confirmado, etc.
            flash(f'Invalid credentials, please try again. ({e})', 'danger')
            return render_template('auth/login.html', email=email)
            
    # Renderiza o template de login
    return render_template('auth/login.html') # Ajustei o caminho do template para seguir sua estrutura

# --- Rota de Logout ---
@auth_bp.route('/logout')
def logout():
    # 3. Invalida a sessão no lado do Supabase
    if 'access_token' in session and supabase:
        try:
            supabase.auth.sign_out()
        except Exception as e:
            # Pode falhar se o token expirou, mas podemos ignorar neste caso de logout
            print(f"Erro ao fazer logout no Supabase: {e}")
    
    # Limpa as informações da sessão do Flask
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('access_token', None)
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))