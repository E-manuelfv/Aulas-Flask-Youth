from flask import Blueprint, render_template, session, flash, redirect, url_for, request, jsonify
from app.models.supabase_client import supabase
from app.controllers.auth import login_required
from .checkout import criar_preferencia

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

def get_cart():
    return session.get("cart", {})

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

def calculate_total():
    cart = get_cart()
    return sum(item["preco"] * item["quantity"] for item in cart.values())

@cart_bp.route('/')
@login_required
def view_cart():
    cart = get_cart()
    total = calculate_total()
    return render_template("cart/cart.html", cart=cart, total=total)

@cart_bp.route('/add-to-cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    cart = get_cart()
    response = supabase.table("produtos").select("*").eq("id", product_id).execute()

    if not response.data:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("main.index"))

    product = response.data[0]

    if product_id in cart:
        cart[product_id]["quantity"] += 1
    else:
        cart[product_id] = {
            "id": str(product["id"]),
            "nome": product["nome"],
            "preco": float(product["preco"]),
            "imagem_url": product.get("imagem_url", ""),
            "quantity": 1
        }

    save_cart(cart)
    flash("Adicionado!", "success")
    return redirect(url_for("main.index"))

@cart_bp.route('/update-cart/<product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    cart = get_cart()
    qty = request.form.get("quantity", type=int)

    if qty <= 0:
        del cart[product_id]
    else:
        cart[product_id]["quantity"] = qty

    save_cart(cart)
    return redirect(url_for("cart.view_cart"))

@cart_bp.route('/remove-from-cart/<product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart = get_cart()
    if product_id in cart:
        del cart[product_id]
    save_cart(cart)
    return redirect(url_for("cart.view_cart"))

@cart_bp.route('/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart.view_cart"))

@cart_bp.route('/checkout')
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash("Carrinho vazio.", "warning")
        return redirect(url_for("cart.view_cart"))

    total = calculate_total()
    return render_template("cart/checkout.html", cart=cart, total=total)

@cart_bp.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    cart = get_cart()

    if not cart:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('cart.view_cart'))

    try:
        # Obter a URL base dinamicamente
        base_url = request.host_url.rstrip('/')
        pagamento_url = criar_preferencia(cart, base_url)
        
        # Redirecionar diretamente para a URL do Mercado Pago
        return redirect(pagamento_url)

    except Exception as e:
        print("Erro no pagamento:", e)
        flash('Erro ao iniciar pagamento. Tente novamente.', 'danger')
        return redirect(url_for('cart.checkout'))

@cart_bp.route('/notification', methods=['POST'])
def payment_notification():
    """Webhook para notificações do Mercado Pago"""
    try:
        data = request.get_json()
        print("NOTIFICAÇÃO RECEBIDA:", data)
        # Aqui você pode processar a notificação de pagamento
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print("Erro na notificação:", e)
        return jsonify({"status": "error"}), 500

@cart_bp.route('/pago')
@login_required
def payment_confirmation():
    session.pop("cart", None)
    flash('Pagamento aprovado! Obrigado pela compra.', 'success')
    return render_template("cart/confirmado_pagamento.html")

@cart_bp.route('/erro')
@login_required
def erro_pagamento():
    flash('Pagamento recusado. Tente novamente.', 'danger')
    return render_template("cart/erro_pagamento.html")

@cart_bp.route('/pendente')
@login_required
def pendente_pagamento():
    flash('Pagamento pendente. Aguarde a confirmação.', 'warning')
    return render_template("cart/pendente_pagamento.html")