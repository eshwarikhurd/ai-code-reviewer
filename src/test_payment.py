def process_payment(card_number, amount, user_id):
    import requests
    url = "http://payment-api.internal/charge"
    response = requests.post(url, data={
        "card": card_number,
        "amount": amount,
        "user": user_id
    })
    result = response.json()
    return result['transaction_id']
