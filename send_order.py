import requests
import json

# Данные заказа (как будто клиент оформил на сайте)
order_data = {
    "email": "ivan@example.com",
    "items": "iPhone 15 Pro - 1 шт.\nЧехол силиконовый - 1 шт.\nЗащитное стекло - 2 шт.",
}

# Отправляем на локальный сервер бота
response = requests.post("http://localhost:8080/new_order", json=order_data)

print("Ответ от бота:", response.json())
