from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.supabase_client import supabase
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../../views/templates/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'] 
        password = request.form['password']
        
        if not supabase:
            flash('Erro de configuração do Supabase.', 'danger')
            return redirect(url_for('auth.register'))

        try:
            supabase.auth.sign_up({"email": email, "password": password})
            flash('Registro completo! Verifique seu Email.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash(f'Falha no registro: {e}', 'danger')
            return render_template('register.html', email=email)
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not supabase:
            flash('Erro de configuração do Supabase.', 'danger')
            return redirect(url_for('auth.login'))
        
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['user_id'] = res.user.id
            session['user_email'] = res.user.email
            session['access_token'] = res.session.access_token
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            flash(f'Credenciais inválidas: {e}', 'danger')
            return render_template('auth/login.html', email=email)
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    if 'access_token' in session and supabase:
        try:
            supabase.auth.sign_out()
        except Exception as e:
            print(f"Erro no logout: {e}")
    
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('access_token', None)
    
    flash('Logout realizado.', 'info')
    return redirect(url_for('auth.login'))