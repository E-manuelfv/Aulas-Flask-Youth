from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models.supabase_client import supabase 
from app.controllers.auth import login_required 
from .services import get_all_products # Importa a lógica de negócio
# from .services import get_user_profile # Adicionando função para o perfil

shop_bp = Blueprint('shop', __name__, url_prefix='/')

# 🏠 ROTA DO CATÁLOGO (INDEX)
@shop_bp.route('/')
def index():
    # 1. TRATAMENTO DE ERRO DE CONFIGURAÇÃO CRÍTICO: 
    # Verifica se o cliente Supabase foi inicializado.
    if not supabase: 
        flash('Erro CRÍTICO: Falha na conexão ou configuração do Supabase. Verifique .env.', 'danger')
        # Retorna lista vazia e exibe a mensagem de erro
        products_list = []
        return render_template('shop/index.html', products=products_list)
        
    # 2. Chama a Lógica de Negócio para buscar todos os produtos
    supabase_response = get_all_products()

    # 3. Processamento da Resposta do Supabase
    if supabase_response and supabase_response.data:
        # Extrai a lista de produtos (Payload do Supabase)
        products_list = supabase_response.data
    else:
        # Trata caso de erro de consulta ou lista vazia
        flash('Não foi possível carregar os produtos. Tente novamente mais tarde.', 'warning')
        products_list = []
        
    # 4. RETORNO DE RESPOSTA VÁLIDA GARANTIDA (View)
    # Usando 'is_authenticated' para o Jinja2
    return render_template(
        'shop/index.html', 
        products=products_list, 
        is_authenticated=('user_id' in session) # Variável para Jinja2
    )

# 👤 ROTA DO PERFIL
@shop_bp.route('/profile')
@login_required # <-- Garante que só usuários logados acessem
def profile():
    # Pega o ID do usuário da sessão (garantido pelo @login_required)
    user_id = session.get('user_id')
    
    if not user_id:
        # Se por algum motivo o ID não estiver na sessão, redireciona (redundante, mas seguro)
        return redirect(url_for('auth.login')) 

    # 1. Chama a lógica de negócio para buscar o perfil customizado
    # profile_data = get_user_profile(user_id) # Assumindo a existência dessa função em services.py

    # if profile_data and profile_data.data:
        # Assumindo que a resposta do Supabase retorna uma lista com 1 perfil
        # user_profile = profile_data.data[0]
    else:
        flash('Não foi possível carregar os dados do seu perfil.', 'danger')
        user_profile = {'username': 'Usuário'} # Objeto padrão de fallback

    # 2. Retorna a View do Perfil
    return render_template('index.html', title='Meu Perfil', profile=user_profile)