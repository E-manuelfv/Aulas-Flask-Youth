from flask import session

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
