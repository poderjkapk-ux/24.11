# utils.py

def parse_products_str(products_str: str) -> dict[str, int]:
    """
    Парсить рядок продуктів у словник {'Назва': кількість}.
    
    Очікуваний формат рядка: 'Бургер x 2, Кола x 1'
    Повертає: {'Бургер': 2, 'Кола': 1}
    
    Використовується в:
    - admin_handlers.py
    - admin_order_management.py
    - notification_manager.py
    - inventory_service.py
    """
    if not products_str:
        return {}
    
    result = {}
    # Розділяємо рядок на окремі позиції по комі з пробілом
    for part in products_str.split(", "):
        try:
            # Шукаємо останній роздільник " x ", щоб коректно обробити назви, що містять "x"
            if " x " in part:
                name, qty_str = part.rsplit(" x ", 1)
                name = name.strip() # Видаляємо зайві пробіли навколо назви
                qty = int(qty_str)
                
                if qty > 0:
                    result[name] = qty
        except ValueError:
            # Ігноруємо частини, які не вдалося розпарсити
            continue
            
    return result