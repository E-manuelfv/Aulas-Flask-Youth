from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from app.models.supabase_client import supabase
from app.controllers.auth import login_required
import mercadopago
import os

# Blueprint principal do carrinho
cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def calculate_total():
    cart = get_cart()
    return sum(item['preco'] * item['quantity'] for item in cart.values())

def prepare_mercadopago_preference_data(cart, base_url):
    """Prepara os dados para a preferência do Mercado Pago"""
    items = []
    
    for index, (product_id, item) in enumerate(cart.items()):
        product_data = {
            "title": str(item.get('nome', 'Produto'))[:127],
            "quantity": int(item.get('quantity', 1)),
            "currency_id": "BRL",
            "unit_price": float(item.get('preco', 0))
        }
        
        imagem_url = item.get('imagem_url', '')
        if imagem_url and imagem_url.startswith(('http://', 'https://')):
            product_data["picture_url"] = str(imagem_url)
        
        items.append(product_data)
    
    preference_data = {
        "items": items,
        "back_urls": {
            "success": f"{base_url}/cart/payment-success",
            "failure": f"{base_url}/cart/payment-failure", 
            "pending": f"{base_url}/cart/payment-pending"
        },
        "auto_return": "approved",
        "binary_mode": True
    }
    
    return preference_data

# ============================================================================
# ROTAS DO CARRINHO
# ============================================================================

@cart_bp.route('/add-to-cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = get_cart()
    
    try:
        response = supabase.table('produtos').select('*').eq('id', product_id).execute()
        if not response.data:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('main.index'))
        
        product = response.data[0]
        
        if product_id in cart:
            cart[product_id]['quantity'] += 1
        else:
            cart[product_id] = {
                'id': str(product['id']),
                'nome': product['nome'],
                'preco': float(product['preco']),
                'imagem_url': product.get('imagem_url', ''),
                'quantity': 1
            }
        
        save_cart(cart)
        flash('Produto adicionado ao carrinho!', 'success')
        
    except Exception as e:
        flash('Erro ao adicionar produto.', 'danger')
        print(f"Erro: {e}")
    
    return redirect(url_for('main.index'))

@cart_bp.route('/')
@login_required
def view_cart():
    cart = get_cart()
    total = calculate_total()
    return render_template('cart/cart.html', 
                         cart=cart, 
                         total=total, 
                         item_count=len(cart))

@cart_bp.route('/remove-from-cart/<product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart = get_cart()
    if product_id in cart:
        del cart[product_id]
        save_cart(cart)
        flash('Produto removido do carrinho.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update-cart/<product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    cart = get_cart()
    quantity = request.form.get('quantity', type=int)
    
    if product_id in cart and quantity > 0:
        cart[product_id]['quantity'] = quantity
        save_cart(cart)
        flash('Quantidade atualizada.', 'success')
    elif product_id in cart and quantity == 0:
        del cart[product_id]
        save_cart(cart)
        flash('Produto removido.', 'success')
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    session.pop('cart', None)
    flash('Carrinho limpo.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    total = calculate_total()
    return render_template('cart/checkout.html', cart=cart, total=total)

# ============================================================================
# ROTAS DE PAGAMENTO (MERCADO PAGO)
# ============================================================================

@cart_bp.route('/create-preference', methods=['POST'])
@login_required
def create_preference():
    try:
        # 1. VERIFICAÇÃO DO TOKEN
        mp_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        if not mp_token:
            return jsonify({'error': 'Token do Mercado Pago não encontrado. Verifique o arquivo .env'}), 500
        
        # 2. INICIALIZAÇÃO DO SDK
        sdk = mercadopago.SDK(mp_token)
        
        # 3. PREPARAR ITENS DO CARRINHO E DADOS DA PREFERÊNCIA
        cart = get_cart()
        base_url = request.host_url.rstrip('/')
        
        # Usa a função auxiliar para montar os dados
        preference_data = prepare_mercadopago_preference_data(cart, base_url)
        
        print(f"DEBUG: Enviando para Mercado Pago - {preference_data}")
        
        # 4. CRIAR PREFERÊNCIA
        preference_response = sdk.preference().create(preference_data)
        
        print(f"DEBUG: Resposta do Mercado Pago - {preference_response}")
        
        # 5. VERIFICAR RESPOSTA
        if 'response' in preference_response and preference_response['response']:
            preference = preference_response["response"]
            return jsonify({
                'success': True,
                'id': preference['id'],
                'init_point': preference['init_point'],
                'sandbox_init_point': preference.get('sandbox_init_point', '')
            })
        else:
            error_msg = preference_response.get('error', 'Erro desconhecido do Mercado Pago')
            print(f"DEBUG: Erro do MP - {error_msg}")
            return jsonify({'error': str(error_msg)}), 500

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Erro completo - {error_trace}")
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

@cart_bp.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    print("Webhook recebido:", data)
    return jsonify({'status': 'ok'})

@cart_bp.route('/payment-success')
@login_required
def payment_success():
    session.pop('cart', None)
    flash('Pagamento aprovado! Obrigado pela sua compra.', 'success')
    return render_template('cart/payment_success.html')

@cart_bp.route('/payment-failure')
@login_required
def payment_failure():
    flash('Pagamento recusado. Tente novamente.', 'danger')
    return render_template('cart/payment_failure.html')

@cart_bp.route('/payment-pending')
@login_required
def payment_pending():
    flash('Pagamento pendente. Aguarde a confirmação.', 'warning')
    return render_template('cart/payment_pending.html')

# Endpoint de teste
@cart_bp.route('/test-integration')
@login_required
def test_integration():
    """Teste simples da integração com Mercado Pago"""
    try:
        mp_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        if not mp_token:
            return jsonify({"status": "error", "message": "Token não encontrado"})
        
        sdk = mercadopago.SDK(mp_token)
        
        # Dados mínimos de teste
        test_preference = {
            "items": [
                {
                    "title": "Produto Teste",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": 10.50
                }
            ]
        }
        
        result = sdk.preference().create(test_preference)
        
        return jsonify({
            "status": "success", 
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })