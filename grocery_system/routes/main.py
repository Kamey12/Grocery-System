from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from flask_login import current_user
from ..models import Product, CartItem

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    featured_products = Product.query.limit(3).all()
    
    if not current_user.is_authenticated:
        return render_template('dashboard.html', featured_products=featured_products)
    
    if current_user.role == 'pending':
        return render_template('dashboard.html', show_role_selection=True)
    
    cart_count = 0
    if current_user.role == 'customer':
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html', 
                          featured_products=featured_products,
                          cart_count=cart_count)

@main_bp.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)