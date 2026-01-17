from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Product, Order

admin_bp = Blueprint('admin', __name__)

def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

@admin_bp.before_request
def restrict_access():
    if not is_admin():
        flash('Unauthorized access')
        return redirect(url_for('main.dashboard'))

@admin_bp.route('/admin/inventory')
def manage_inventory():
    products = Product.query.all()
    return render_template('admin/inventory.html', products=products)

@admin_bp.route('/admin/orders')
def view_orders():
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/admin/order/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Order status updated')
    return redirect(url_for('admin.view_orders'))

@admin_bp.route('/admin/product/add', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    category = request.form['category']
    image_url = request.form.get('image_url', 'images/products/default.jpg')
    
    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        image_url=image_url
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully')
    return redirect(url_for('admin.manage_inventory'))

@admin_bp.route('/admin/product/<int:product_id>/edit', methods=['POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.name = request.form['name']
    product.description = request.form['description']
    product.price = float(request.form['price'])
    product.stock = int(request.form['stock'])
    product.category = request.form['category']
    if 'image_url' in request.form:
        product.image_url = request.form['image_url']
    
    db.session.commit()
    flash('Product updated successfully')
    return redirect(url_for('admin.manage_inventory'))