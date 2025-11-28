from flask import render_template, request, flash, session, jsonify
from app.controllers.auth import login_required
from cart import cart_bp
from .aux_functions import get_cart, prepare_mercadopago_preference_data
import mercadopago
import os

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