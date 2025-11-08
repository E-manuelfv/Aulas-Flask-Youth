from flask import (render_template, request, redirect, url_for, 
                   flash, Blueprint)
from flask_login import login_user, logout_user, current_user
# CORREÇÃO AQUI: Importamos User E users_db para acessar o dicionário global
from app.models import User, users_db  

# 1. Cria a instância do Blueprint
bp = Blueprint('auth', __name__, template_folder='../views/templates/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 1. Validação: Checa se os campos estão preenchidos
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('register.html', title='Register Page')
            
        # 2. Validação: Email já cadastrado
        if User.get_by_email(email):
            flash('Este email já está cadastrado. Tente fazer login.', 'danger')
            return render_template('register.html', title='Register Page')

        # 3. Cria o novo usuário e o salva no DB (simulado)
        # CORREÇÃO DA LINHA DO ERRO: Usa users_db diretamente.
        new_id = len(users_db) + 1 
        new_user = User(id=new_id, email=email, password=password)
        User.save(new_user)
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
        
    # Método GET
    return render_template('register.html', title='Register Page')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 2. Busca o usuário no "banco"
        user = User.get_by_email(email)
        
        # 3. Valida o usuário e a senha (com hash!)
        if user is None or not user.check_password(password):
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('auth.login'))
        
        # 4. SUCESSO!
        login_user(user, remember=True)
        
        # Pega a URL que o usuário tentou acessar antes de ser redirecionado para o login
        next_page = request.args.get('next')
        flash('Login realizado com sucesso!', 'success')
        return redirect(next_page or url_for('main.index'))

    # Método GET
    return render_template('login.html', title='Login Page')


@bp.route('/logout')
def logout():
    # 5. O Flask-Login limpa a sessão
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))
