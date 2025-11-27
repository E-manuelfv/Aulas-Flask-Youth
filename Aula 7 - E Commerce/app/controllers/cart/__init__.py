from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from app.models.supabase_client import supabase
from app.controllers.auth import login_required

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

# Rota para adicionar item ao carrinho
@cart_bp.route('/add-to-cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # Lógica para adicionar o produto ao carrinho na sessão
    # Recuperar o carrinho da sessão (se existir) ou criar um novo
    cart = session.get('cart', {})
    
    # Verificar se o produto já está no carrinho
    if product_id in cart:
        # Se já estiver, incrementa a quantidade
        cart[product_id]['quantity'] += 1
    else:
        # Se não, busca os dados do produto no Supabase
        try:
            response = supabase.table('produtos').select('*').eq('id', product_id).execute()
            if response.data:
                product = response.data[0]
                cart[product_id] = {
                    'id': product['id'],
                    'nome': product['nome'],
                    'preco': product['preco'],
                    'imagem_url': product['imagem_url'],
                    'quantity': 1
                }
            else:
                flash('Produto não encontrado.', 'danger')
                return redirect(url_for('main.index'))
        except Exception as e:
            flash('Erro ao adicionar produto ao carrinho.', 'danger')
            return redirect(url_for('main.index'))
    
    # Atualiza o carrinho na sessão
    session['cart'] = cart
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('main.index'))

# Rota para visualizar o carrinho
@cart_bp.route('/')
@login_required
def view_cart():
    cart = session.get('cart', {})
    total = 0
    for item in cart.values():
        total += item['preco'] * item['quantity']
    return render_template('cart/cart.html', cart=cart, total=total, is_authenticated=('user_id' in session))

# Rota para remover item do carrinho
@cart_bp.route('/remove-from-cart/<product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        flash('Produto removido do carrinho.', 'success')
    else:
        flash('Produto não encontrado no carrinho.', 'danger')
    return redirect(url_for('cart.view_cart'))

# Rota para atualizar a quantidade de um item no carrinho
@cart_bp.route('/update-cart/<product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    cart = session.get('cart', {})
    quantity = request.form.get('quantity', type=int)
    if product_id in cart and quantity and quantity > 0:
        cart[product_id]['quantity'] = quantity
        session['cart'] = cart
        flash('Quantidade atualizada.', 'success')
    elif product_id in cart and quantity == 0:
        # Remove o item se a quantidade for 0
        del cart[product_id]
        session['cart'] = cart
        flash('Produto removido do carrinho.', 'success')
    else:
        flash('Erro ao atualizar a quantidade.', 'danger')
    return redirect(url_for('cart.view_cart'))

# Rota para limpar o carrinho
@cart_bp.route('/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    session.pop('cart', None)
    flash('Carrinho limpo.', 'success')
    return redirect(url_for('cart.view_cart'))

# Rota para checkout (iniciar processo de pagamento)
@cart_bp.route('/checkout')
@login_required
def checkout():
    # Aqui vamos integrar com o Mercado Pago
    # Por enquanto, apenas redireciona para a página de checkout (a ser implementada)
    return render_template('cart/checkout.html')

# Lógica de integração com Mercado Pago será implementada aqui
import mercadopago
import os

@cart_bp.route('/create-preference', methods=['POST'])
@login_required
def create_preference():
    cart = session.get('cart', {})
    if not cart:
        flash('Carrinho vazio.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    # Configura o Mercado Pago
    sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN"))
    
    # Cria os itens para a preferência
    items = []
    for item in cart.values():
        items.append({
            "title": item['nome'],
            "quantity": item['quantity'],
            "currency_id": "BRL",
            "unit_price": float(item['preco'])
        })
    
    # Cria a preferência
    preference_data = {
        "items": items,
        "back_urls": {
            "success": url_for('cart.payment_success', _external=True),
            "failure": url_for('cart.payment_failure', _external=True),
            "pending": url_for('cart.payment_pending', _external=True)
        },
        "auto_return": "approved",
    }
    
    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        return redirect(preference["init_point"])
    except Exception as e:
        flash('Erro ao processar o pagamento.', 'danger')
        return redirect(url_for('cart.view_cart'))

@cart_bp.route('/payment-success')
@login_required
def payment_success():
    # Limpa o carrinho após sucesso
    session.pop('cart', None)
    flash('Pagamento aprovado! Obrigado pela compra.', 'success')
    return redirect(url_for('main.index'))

@cart_bp.route('/payment-failure')
@login_required
def payment_failure():
    flash('Pagamento recusado.', 'danger')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/payment-pending')
@login_required
def payment_pending():
    flash('Pagamento pendente.', 'warning')
    return redirect(url_for('cart.view_cart'))