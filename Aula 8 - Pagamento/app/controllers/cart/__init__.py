from flask import Blueprint 

# O nome do Blueprint DEVE ser 'cart'
cart_bp = Blueprint('cart', __name__, url_prefix='/cart') 

@cart_bp.route('/add-to-cart/<product_id>')
# O nome da função DEVE ser 'add_to_cart'
def add_to_cart(product_id): 
    # ... sua lógica de sessão aqui
    return 'Produto adicionado ao carrinho!' # Exemplo