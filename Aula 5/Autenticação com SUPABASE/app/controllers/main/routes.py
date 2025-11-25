from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__, template_folder='../views/templates')

@bp.route('/')
@bp.route('/index')
def index():
    # current_user está disponível globalmente!
    return render_template('index.html', title='Home Page', user=current_user)

@bp.route('/profile')
@login_required # <-- Apenas usuários logados podem acessar!
def profile():
    """
    Se o usuário não estiver logado, o Flask-Login o redireciona para 'auth.login'
    com o parâmetro ?next=/profile.
    """
    # Se chegou aqui, o usuário ESTÁ logado.
    return render_template('profile.html', title='Meu Perfil', user=current_user)