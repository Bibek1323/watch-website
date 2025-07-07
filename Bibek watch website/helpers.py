from flask_login import current_user
from .models import CartItem
from .data import get_watch_by_id

def get_mini_cart_data():
    if not current_user.is_authenticated:
        return [], 0
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    mini_cart = []
    total = 0
    for item in items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            mini_cart.append({'watch': watch, 'item': item})
            total += watch['price'] * item.quantity
    return mini_cart, total
