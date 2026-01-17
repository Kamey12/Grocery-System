from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Product, CartItem, Order, OrderItem

store_bp = Blueprint('store', __name__)

@store_bp.route('/products')
def browse_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@store_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@store_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    if current_user.role != 'customer':
        flash('Only customers can add items to cart')
        return redirect(url_for('store.browse_products'))

    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    
    if quantity > product.stock:
        flash(f'Only {product.stock} units available')
        return redirect(url_for('store.browse_products'))
    
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added to cart')
    return redirect(url_for('store.view_cart'))

@store_bp.route('/cart')
@login_required
def view_cart():
    if current_user.role != 'customer':
        flash('Only customers can view cart')
        return redirect(url_for('main.dashboard'))

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@store_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('store.view_cart'))

    quantity = int(request.form.get('quantity', 1))
    if quantity > cart_item.product.stock:
        flash(f'Only {cart_item.product.stock} units available')
        quantity = cart_item.product.stock

    cart_item.quantity = quantity
    db.session.commit()
    flash('Cart updated')
    return redirect(url_for('store.view_cart'))

@store_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart')
    return redirect(url_for('store.view_cart'))

@store_bp.route('/checkout')
@login_required
def checkout():
    if current_user.role != 'customer':
        return redirect(url_for('main.dashboard'))
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('store.view_cart'))
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@store_bp.route('/checkout/process', methods=['POST'])
@login_required
def process_checkout():
    if current_user.role != 'customer':
        flash('Only customers can process checkout')
        return redirect(url_for('main.dashboard'))

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('store.view_cart'))

    address = request.form.get('address')
    phone = request.form.get('phone')

    current_user.address = address
    current_user.phone = phone
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status='processing'
    )
    db.session.add(order)
    
    db.session.flush() 

    
    try:
        # Create order items and update stock
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                raise ValueError(f'Insufficient stock for {cart_item.product.name}')
            
            order_item = OrderItem(
                order_id=order.id, 
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
            
            # Remove cart item
            db.session.delete(cart_item)
        
        db.session.commit()
        flash('Order placed successfully!')
        return redirect(url_for('store.track_order', order_id=order.id))
        
    except ValueError as e:
        db.session.rollback()
        flash(str(e))
        return redirect(url_for('store.view_cart'))
    except Exception as e:
        db.session.rollback()
        print(f"Error processing order: {e}") 
        flash('An error occurred while processing your order')
        return redirect(url_for('store.view_cart'))
    
@store_bp.route('/order/track/<int:order_id>')
@login_required
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('main.dashboard'))
    return render_template('track_order.html', order=order)

@store_bp.route('/my-orders')
@login_required
def my_orders():
    # Get orders for current user, newest first
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)