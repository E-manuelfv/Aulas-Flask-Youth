from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models.supabase_client import supabase 
from app.controllers.auth import login_required 
from .services import get_all_products
# from .services import get_user_profile # Adicionando função para o perfil

main_bp = Blueprint('main', __name__, url_prefix='/')

# ROTA DO CATÁLOGO (INDEX)
@main_bp.route('/')
def index():
    if not supabase: 
        flash('Erro CRÍTICO: Falha na conexão ou configuração do Supabase. Verifique .env.', 'danger')
        products_list = []
        return render_template('main/index.html', products=products_list)
    
    supabase_response = get_all_products()

    if supabase_response and supabase_response.data:
        products_list = supabase_response.data
    else:
        flash('Não foi possível carregar os produtos. Tente novamente mais tarde.', 'warning')
        products_list = []
        
    return render_template(
        'main/index.html', 
        products=products_list, 
        is_authenticated=('user_id' in session)
    )

@main_bp.route('/profile')
@login_required 
def profile():
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('auth.login')) 
    else:
        flash('Não foi possível carregar os dados do seu perfil.', 'danger')
        user_profile = {'username': 'Usuário'}

    return render_template('index.html', title='Meu Perfil', profile=user_profile)