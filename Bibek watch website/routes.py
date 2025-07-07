# app/routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from flask import jsonify
from flask_login import login_required, current_user
from .models import CartItem  
from flask import session
from .data import get_watch_by_id
#from app.extensions import mail
from flask_mail import Message
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Address
import os



from .models import User, WishlistItem, CartItem, Order, OrderItem, Coupon
from .forms import SignupForm, LoginForm, ContactForm, AddressForm
from .extensions import db, login_manager,mail
from . import data

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_watch_by_id(watch_id):
    return next((w for w in data.watches if w["id"] == watch_id), None)

# ROUTES BELOW


@main.route("/")
def root_redirect():
    return redirect(url_for('main.intro'))
@main.route("/intro")
def intro():
    print(" /intro route triggered")
    return render_template("intro.html")

@main.route("/home")
def home():
    categories_info = [
        {
            "name": "Heritage Classic",
            "description": "Timeless designs reflecting traditional elegance and craftsmanship.",
            "image": "images/heritage.jpg"
        },
        {
            "name": "Sports Elite",
            "description": "High-performance timepieces built for the active and adventurous.",
            "image": "images/sports.jpg"
        },
        {
            "name": "Grand Complications",
            "description": "Sophisticated watches with complex mechanical features and luxury.",
            "image": "images/grand.jpg"
        }
    ]
    mini_cart, mini_total = get_mini_cart()

    return render_template("home.html", mini_cart=mini_cart, mini_total=mini_total, categories=categories_info)

@main.route("/category/<category>")
def category_detail(category):
    category = category.replace("-", " ")
    filtered = [w for w in data.watches if w["category"] == category][:5]
    if not filtered:
        return render_template("404.html"), 404
    return render_template("category_detail.html", watches=filtered, category=category)

@main.route("/watches")
def watches():
    selected_brand = request.args.get("brand")
    selected_category = request.args.get("category")
    filtered_watches = data.watches
    if selected_brand:
        filtered_watches = [w for w in filtered_watches if w.get("brand") == selected_brand]
    if selected_category:
        filtered_watches = [w for w in filtered_watches if w.get("category") == selected_category]

    return render_template("watches.html", watches=filtered_watches, brands=data.brands, categories=data.categories,
                           selected_brand=selected_brand, selected_category=selected_category)

@main.route("/watch/<int:watch_id>")
def watch_detail(watch_id):
    selected_watch = next((w for w in data.watches if w['id'] == watch_id), None)
    if selected_watch is None:
        return render_template("404.html"), 404
    return render_template("watch_detail.html", watch=selected_watch)

@main.route("/about")
def about():
    return render_template("about.html")


from flask_mail import Message
from flask import request, render_template, flash, redirect, url_for
from . import mail  # make sure mail is imported from app/__init__.py
from .forms import ContactForm  # ensure this is present
from flask_mail import Message

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        sender_email = form.email.data
        message = form.message.data

        msg = Message(subject="New Contact Message",
                      sender=sender_email,
                      recipients=['youradminemail@gmail.com'])
        msg.body = f"""
You received a new contact message:

Name: {name}
Email: {sender_email}
Message:
{message}
"""
        try:
            mail.send(msg)
            flash("Your message has been sent!", "success")
        except Exception as e:
            flash("Failed to send message. Please try again.", "danger")
            print("Mail error:", e)

        return redirect(url_for('main.contact'))

    return render_template("contact.html", form=form)



@main.route("/cart/add/<int:watch_id>")
@login_required
def add_to_cart(watch_id):
    watch = get_watch_by_id(watch_id)
    if not watch:
        return "Watch not found", 404

    existing = CartItem.query.filter_by(user_id=current_user.id, watch_id=watch_id).first()
    if existing:
        existing.quantity += 1
    else:
        existing = CartItem(user_id=current_user.id, watch_id=watch_id, quantity=1)
        db.session.add(existing)

    db.session.commit()
    flash("Watch added to cart!", "success")
    return redirect(url_for("main.cart"))

@main.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    cart_details = []
    total = 0

    for item in items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            subtotal = watch['price'] * item.quantity
            total += subtotal
            cart_details.append({
                'item': item,
                'watch': watch,
                'subtotal': subtotal
            })

    return render_template("cart.html", cart_details=cart_details, total=total)


@main.context_processor
def inject_cart_data():
    if 'user_id' in session:
        user_id = session['user_id']
        cart_items = CartItem.query.filter_by(user_id=user_id).all()

        mini_cart = []
        total = 0

        for item in cart_items:
            watch = get_watch_by_id(item.watch_id)
            if watch:
                mini_cart.append({'watch': watch, 'item': item})
                total += watch['price'] * item.quantity

        return dict(mini_cart=mini_cart, mini_total=total)
    return dict(mini_cart=[], mini_total=0)

@main.route("/cart/increase/<int:item_id>")
def increase_quantity(item_id):
    item = CartItem.query.get_or_404(item_id)
    item.quantity += 1
    db.session.commit()
    return redirect(url_for('main.cart'))

@main.route("/cart/decrease/<int:item_id>")
def decrease_quantity(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.quantity > 1:
        item.quantity -= 1
        db.session.commit()
    return redirect(url_for('main.cart'))

@main.route("/cart/remove/<int:item_id>")
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.cart'))

def get_mini_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all() if current_user.is_authenticated else []
    cart = []
    total = 0
    for item in items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            cart.append({"watch": watch, "item": item})
            total += watch["price"] * item.quantity
    return cart, total


@main.route('/api/cart')
@login_required
def api_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    result = []
    for item in cart_items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            result.append({
                "id": item.id,
                "watch_id": watch["id"],
                "name": watch["name"],
                "price": watch["price"],
                "quantity": item.quantity,
                "image": watch["image"]
            })
    return jsonify(result)





@main.route('/checkout', methods=['GET'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    watches = []
    total_price = 0

    for item in cart_items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            subtotal = item.quantity * watch['price']
            total_price += subtotal
            watches.append(watch)

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('main.cart'))

    discount = round(total_price * 0.05)
    final_total = total_price - discount

    address = Address.query.filter_by(user_id=current_user.id).first()
    address_data = {
        'name': address.name if address else '',
        'phone': address.phone if address else '',
        'address_line': address.address_line if address else '',
        'city': address.city if address else '',
        'state': address.state if address else '',
        'pincode': address.pincode if address else '',
    }

    zipped_items = zip(cart_items, watches)
    return render_template("checkout.html", cart_items=cart_items, watches=watches, total=final_total,
                           discount=discount, address=address_data, zipped_items=zipped_items)



@main.route('/buy/<int:watch_id>')
def buy_watch(watch_id):
    watch = get_watch_by_id(watch_id)
    if not watch:
        flash("Watch not found.", "danger")
        return redirect(url_for('main.watches'))

    if current_user.is_authenticated:
        existing = CartItem.query.filter_by(user_id=current_user.id, watch_id=watch_id).first()
        if existing:
            existing.quantity += 1
        else:
            new_item = CartItem(user_id=current_user.id, watch_id=watch_id, quantity=1)
            db.session.add(new_item)
        db.session.commit()
        flash("Item added to your cart!", "success")
    else:
        cart = session.get('cart', {})
        watch_id_str = str(watch_id)
        cart[watch_id_str] = cart.get(watch_id_str, 0) + 1
        session['cart'] = cart
        session.modified = True
        flash("Item added to cart (guest session)", "success")

    return redirect(url_for('main.checkout'))




@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for("main.login"))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Successfully registered!", "success")
        return redirect(url_for("main.login"))
    return render_template("signup.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back {user.username}!", "success")
            return redirect(url_for("main.home"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.")
    return redirect(url_for("main.home"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_watch_by_id(watch_id):
    return next((w for w in data.watches if w["id"] == watch_id), None)

@main.route("/wishlist/add/<int:watch_id>")
@login_required
def add_to_wishlist(watch_id):
    watch = get_watch_by_id(watch_id)
    if not watch:
        return "Watch not found", 404
    existing = WishlistItem.query.filter_by(user_id=current_user.id, watch_id=watch_id).first()
    if existing:
        flash("Already in wishlist.", "info")
    else:
        item = WishlistItem(user_id=current_user.id, watch_id=watch_id)
        db.session.add(item)
        db.session.commit()
        flash("Watch added to wishlist!", "success")
    return redirect(url_for("main.wishlist"))

@main.route("/wishlist")
@login_required
def wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    watches = []
    for item in wishlist_items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            watches.append(watch)
    return render_template("wishlist.html", watches=watches)


@main.route("/wishlist/remove/<int:watch_id>", methods=["POST"])
@login_required
def remove_from_wishlist(watch_id):
    item = WishlistItem.query.filter_by(user_id=current_user.id, watch_id=watch_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Watch removed from your wishlist.", "success")
    else:
        flash("Watch not found in your wishlist.", "warning")
    return redirect(url_for("main.wishlist"))


@main.route("/accounts")
def accounts():
    all_users = User.query.all()
    return render_template("accounts.html", users=all_users)

@main.route('/order-confirmation')
@login_required
def order_confirmation():
    # ✅ Fetch latest order
    order = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).first()
    if not order:
        flash("No recent orders found.", "warning")
        return redirect(url_for('main.home'))

    # ✅ Get order items and watch details
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    watches = []
    for item in order_items:
        watch = get_watch_by_id(item.watch_id)
        if watch:
            watch['quantity'] = 1  # Default quantity
            watches.append(watch)

    # ✅ Fetch address
    address = Address.query.filter_by(user_id=current_user.id).first()

    # ✅ Calculate discount and original total
    total = order.total_price
    if order.payment_method == "Online":
        discount = round(total / 0.95 * 0.05)
        original_total = total + discount
    else:  # COD
        discount = round(total * 0.05)
        original_total = round(total / 0.95)

    # ✅ Pass data to template
    return render_template("order_confirmation.html",
                           user=current_user,
                           address=address,
                           watches=watches,
                           total=original_total,
                           discount=discount,
                           total_after_discount=total,
                           payment_method=order.payment_method,
                           timestamp=order.timestamp)


@main.route('/account')
@login_required
def account():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    address = Address.query.filter_by(user_id=current_user.id).first()
    return render_template('account.html', user=current_user, orders=orders, address=address)

@main.route('/update-address', methods=['GET', 'POST'])
@login_required
def update_address():
    # Always define it first
    address_data = Address.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        if not address_data:
            address_data = Address(user_id=current_user.id)

        address_data.name = request.form.get('name')
        address_data.phone = request.form.get('phone')
        address_data.address_line = request.form.get('address_line')
        address_data.city = request.form.get('city')
        address_data.state = request.form.get('state')
        address_data.pincode = request.form.get('pincode')
        address_data.country = request.form.get('country')

        db.session.add(address_data)
        db.session.commit()
        flash("Address updated!", "success")
        return redirect(url_for('main.account'))

    return render_template("update_address.html", address=address_data)


@main.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form['current_password']
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']
        
        if not check_password_hash(current_user.password_hash, current_pw):
            flash("Current password is incorrect.", "danger")
        elif new_pw != confirm_pw:
            flash("Passwords do not match.", "warning")
        else:
            current_user.password = generate_password_hash(new_pw)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for('main.account'))
    return render_template('change_password.html')

@main.route('/account/address', methods=['GET', 'POST'])
@login_required
def manage_address():
    form = AddressForm()
    existing = Address.query.filter_by(user_id=current_user.id).first()

    if form.validate_on_submit():
        if existing:
            existing.name = form.name.data
            existing.phone = form.phone.data
            existing.address = form.address.data
            existing.pincode = form.pincode.data
            existing.city = form.city.data
            existing.state = form.state.data
        else:
            new_address = Address(
                user_id=current_user.id,
                name=form.name.data,
                phone=form.phone.data,
                address=form.address.data,
                pincode=form.pincode.data,
                city=form.city.data,
                state=form.state.data
            )
            db.session.add(new_address)
        db.session.commit()
        flash("Address saved successfully!", "success")
        return redirect(url_for('main.account'))

    # Pre-fill if address exists
    if existing and request.method == 'GET':
        form.name.data = existing.name
        form.phone.data = existing.phone
        form.address.data = existing.address
        form.pincode.data = existing.pincode
        form.city.data = existing.city
        form.state.data = existing.state

    return render_template("address_form.html", form=form)

@main.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('main.account'))

    if order.status != 'Pending':
        flash("Only pending orders can be cancelled.", "warning")
        return redirect(url_for('main.account'))

    order.status = 'Cancelled'
    msg = Message(
    "Order Cancelled - Timora",
    sender="your_email@gmail.com",
    recipients=[current_user.email]
    )
    msg.body = f"Hi {current_user.username},\nYour order #{order.id} has been successfully cancelled."
    mail.send(msg)

    db.session.commit()
    flash("Your order has been cancelled.", "success")
    return redirect(url_for('main.account'))


@main.route('/payment')
@login_required
def payment():
    return render_template("payment.html")

@main.route('/payment-gateway')
@login_required
def payment_gateway():
    total = session.get('payment_total', 0)
    return render_template("payment_gateway.html", total=total)




@main.route('/online-payment/<int:order_id>')
@login_required
def online_payment(order_id):
    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id:
        flash("No pending order found.", "danger")
        return redirect(url_for('main.checkout'))

    return render_template('online_payment.html', order=order)

@main.route('/confirm-cod-order', methods=['POST'])
@login_required
def confirm_cod_order():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address_line = request.form.get('address')
    city = request.form.get('district')
    state = request.form.get('state')
    pincode = request.form.get('pincode')

    address = Address.query.filter_by(user_id=current_user.id).first()
    if not address:
        address = Address(user_id=current_user.id)
    address.name = name
    address.phone = phone
    address.address_line = address_line
    address.city = city
    address.state = state
    address.pincode = pincode

    db.session.add(address)
    db.session.commit()

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Cart is empty.", "warning")
        return redirect(url_for('main.cart'))

    total = sum(get_watch_by_id(item.watch_id)['price'] * item.quantity for item in cart_items)
    discount = round(total * 0.05)
    final_price = total - discount

    order = Order(user_id=current_user.id, total_price=final_price, payment_method='COD', status='Pending')
    db.session.add(order)
    db.session.commit()

    for item in cart_items:
        db.session.add(OrderItem(order_id=order.id, watch_id=item.watch_id, quantity=item.quantity))
    db.session.commit()

    for item in cart_items:
        db.session.delete(item)
    db.session.commit()

    # ✅ Send Confirmation Email
    msg = Message("📦 Timora Order Placed - Cash on Delivery",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[current_user.email])
    msg.body = f"""
Hi {current_user.username},

✅ Your order has been successfully placed with Cash on Delivery!

🧾 Payment Method: Cash on Delivery (COD)
📦 Order Amount: ₹{final_price}
📍 Shipping Address: {address.name}, {address.address_line}, {address.city}, {address.state} - {address.pincode}
📞 Phone: {address.phone}

We will ship your order shortly. Thank you for choosing Timora!

🕰️ Timora Team
"""
    mail.send(msg)

    flash("✅ COD Order placed successfully! Confirmation email sent.", "success")
    return redirect(url_for('main.order_confirmation'))



@main.route('/qr-payment')
@login_required
def qr_payment():
    total = session.get('final_price')
    if not total:
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for('main.home'))

    return render_template('qr_payment.html', total=total)



@main.route('/payment')
@login_required
def show_qr_payment():
    return render_template('qr_payment.html')


@main.route('/initiate-online-order', methods=['POST'])
@login_required
def initiate_online_order():
    # 1. Get form data
    name = request.form.get('name')
    phone = request.form.get('phone')
    address_line = request.form.get('address')
    city = request.form.get('district')
    state = request.form.get('state')
    pincode = request.form.get('pincode')

    # 2. Save or update address
    address = Address.query.filter_by(user_id=current_user.id).first()
    if not address:
        address = Address(user_id=current_user.id)

    address.name = name
    address.phone = phone
    address.address_line = address_line
    address.city = city
    address.state = state
    address.pincode = pincode
    db.session.add(address)
    db.session.commit()

    # 3. Fetch cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("❌ Cart is empty.", "danger")
        return redirect(url_for('main.cart'))

    # 4. Calculate total and discount
    total = sum(get_watch_by_id(item.watch_id)['price'] * item.quantity for item in cart_items)
    discount = round(total * 0.05)
    final_price = total - discount  # <-- This is now defined

    # 5. Create a pending order (status will be updated on confirmation)
    order = Order(user_id=current_user.id, total_price=final_price, payment_method='Online', status='Pending')
    db.session.add(order)
    db.session.commit()

    # 6. Create order items
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, watch_id=item.watch_id, quantity=item.quantity)
        db.session.add(order_item)

    db.session.commit()

    # 7. Store order ID temporarily in session
    session['pending_order_id'] = order.id

    # 8. Redirect to QR page
    return redirect(url_for('main.qr_payment'))


@main.route('/confirm-online-order', methods=['GET', 'POST'])  # not POST
@login_required
def confirm_online_order():
    # Confirm pending online order
    order_id = session.get('pending_order_id')

    if not order_id:
        flash("❌ No pending order found.", "danger")
        return redirect(url_for('main.account'))

    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id or order.status != 'Pending':
        flash("❌ Invalid order or already processed.", "danger")
        return redirect(url_for('main.account'))

    # Update order status to 'Paid'
    order.status = 'Paid'
    db.session.commit()

    # Delete cart items
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    # Clear session
    session.pop('pending_order_id', None)

    # Send email (optional)
    msg = Message("✅ Payment Received – Timora",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[current_user.email])
    msg.body = f"""
Hi {current_user.username},

✅ Your payment of ₹{order.total_price} was successfully received.

📦 Order ID: {order.id}
🧾 Payment Mode: Online
🕒 Status: Paid

Thank you for shopping with Timora!
"""
    mail.send(msg)

    flash("✅ Online payment confirmed. Confirmation email sent!", "success")
    return redirect(url_for('main.order_confirmation'))

@main.route("/debug")
def debug():
    heritage_count = len([w for w in data.watches if w['category'] == 'Heritage Classic'])
    sports_count = len([w for w in data.watches if w['category'] == 'Sports Elite'])
    complications_count = len([w for w in data.watches if w['category'] == 'Grand Complications'])
    return f"""
    <h2>Debug Info</h2>
    <p>Total watches: {len(data.watches)}</p>
    <p>Categories: {data.categories}</p>
    <p>Brands: {data.brands}</p>
    <ul>
        <li>Heritage Classic: {heritage_count}</li>
        <li>Sports Elite: {sports_count}</li>
        <li>Grand Complications: {complications_count}</li>
    </ul>


     """
 

 
