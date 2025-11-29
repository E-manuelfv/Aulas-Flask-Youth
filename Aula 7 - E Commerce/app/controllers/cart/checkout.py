import mercadopago
import os

def criar_preferencia(cart, base_url):
    """
    Versão simplificada que deve funcionar
    """
    ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not ACCESS_TOKEN:
        raise Exception("Token do Mercado Pago não configurado")
    
    sdk = mercadopago.SDK(ACCESS_TOKEN)

    # Item único e simples para teste
    items = [{
        "title": "Compra na Loja",
        "quantity": 1,
        "unit_price": float(sum(item["preco"] * item["quantity"] for item in cart.values())),
        "currency_id": "BRL"
    }]

    # Dados MÍNIMOS - sem auto_return, sem URLs complexas
    preference_data = {
        "items": items
        # Removemos back_urls e auto_return temporariamente
    }

    print("DEBUG - Dados SIMPLIFICADOS enviados:", preference_data)

    result = sdk.preference().create(preference_data)
    print("DEBUG - Resposta SIMPLIFICADA:", result)

    if 'response' in result and 'init_point' in result['response']:
        return result['response']['init_point']
    else:
        # Tentativa alternativa com sandbox
        if 'response' in result and 'sandbox_init_point' in result['response']:
            return result['response']['sandbox_init_point']
        else:
            raise Exception("Não foi possível obter URL de pagamento")