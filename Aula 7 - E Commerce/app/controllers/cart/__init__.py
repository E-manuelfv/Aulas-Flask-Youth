from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from app.models.supabase_client import supabase
from app.controllers.auth import login_required

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

def get_cart():
    """Retorna o carrinho da sessão ou dicionário vazio"""
    return session.get('cart', {})

def save_cart(cart):
    """Salva o carrinho na sessão"""
    session['cart'] = cart
    session.modified = True

def calculate_total():
    """Calcula o total do carrinho"""
    cart = get_cart()
    return sum(item['preco'] * item['quantity'] for item in cart.values())

@cart_bp.route('/add-to-cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Adiciona produto ao carrinho"""
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
    """Exibe a página do carrinho"""
    cart = get_cart()
    total = calculate_total()
    return render_template('cart/cart.html', 
                         cart=cart, 
                         total=total, 
                         item_count=len(cart))

@cart_bp.route('/remove-from-cart/<product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    """Remove produto do carrinho"""
    cart = get_cart()
    if product_id in cart:
        del cart[product_id]
        save_cart(cart)
        flash('Produto removido do carrinho.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update-cart/<product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    """Atualiza quantidade do produto no carrinho"""
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
    """Limpa todo o carrinho"""
    session.pop('cart', None)
    flash('Carrinho limpo.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
@login_required
def checkout():
    """Página de checkout - PRONTA PARA INTEGRAÇÃO COM GATEWAY"""
    cart = get_cart()
    if not cart:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    total = calculate_total()
    return render_template('cart/checkout.html', cart=cart, total=total)

# ============================================================================
# ROTAS DE PAGAMENTO - ESPAÇO PARA FUTURA INTEGRAÇÃO
# ============================================================================

@cart_bp.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    """
    ENDPOINT PARA FUTURA INTEGRAÇÃO COM GATEWAY DE PAGAMENTO
    
    Aqui você pode integrar com:
    - Mercado Pago
    - Stripe
    - PayPal
    - PagSeguro
    - Ou qualquer outro gateway
    
    Retorno esperado:
    - Sucesso: Redirecionar para confirmation
    - Falha: Retornar para checkout com erro
    """
    # TODO: Implementar lógica de pagamento
    flash('Sistema de pagamento em desenvolvimento.', 'info')
    return redirect(url_for('cart.checkout'))

@cart_bp.route('/payment-confirmation')
@login_required
def payment_confirmation():
    """Página de confirmação de pagamento bem-sucedido"""
    session.pop('cart', None)  # Limpa carrinho após compra
    return render_template('cart/payment_confirmation.html')