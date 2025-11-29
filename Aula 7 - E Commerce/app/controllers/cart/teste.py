import mercadopago
sdk = mercadopago.SDK("APP_USR-5653152832102492-112822-e3c28abefc60eb8a40f87587e6146f5d-3021017043")

res = sdk.preference().create({
    "items": [{
        "title": "Teste",
        "quantity": 1,
        "unit_price": 10
    }]
})

print(res["response"]["init_point"])
