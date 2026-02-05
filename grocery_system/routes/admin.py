import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..models import db, Product, Order

admin_bp = Blueprint('admin', __name__)

def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

@admin_bp.before_request
def restrict_access():
    if not is_admin():
        flash('Unauthorized access')
        return redirect(url_for('main.dashboard'))

# --- Helper function for image upload ---
def save_image(file):
    if file:
        filename = secure_filename(file.filename)
        # Check if extension is allowed (optional but recommended)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Save inside static/images/products
            file_path = os.path.join(current_app.root_path, 'static', 'images', 'products', filename)
            file.save(file_path)
            return f'images/products/{filename}'
    return None

@admin_bp.route('/admin/inventory')
def manage_inventory():
    products = Product.query.all()
    return render_template('admin/inventory.html', products=products)

@admin_bp.route('/admin/orders')
def view_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/admin/order/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Order status updated')
    return redirect(url_for('admin.view_orders'))

# --- CRUD: CREATE ---
@admin_bp.route('/admin/product/add', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    category = request.form['category']
    
    # Handle Image Upload
    image_file = request.files.get('image_file')
    image_url = save_image(image_file) or 'images/products/default.jpg'
    
    product = Product(
        name=name, description=description, price=price,
        stock=stock, category=category, image_url=image_url
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully')
    return redirect(url_for('admin.manage_inventory'))

# --- CRUD: UPDATE ---
@admin_bp.route('/admin/product/<int:product_id>/edit', methods=['POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.name = request.form['name']
    product.description = request.form['description']
    product.price = float(request.form['price'])
    product.stock = int(request.form['stock'])
    product.category = request.form['category']
    
    # Check if new image was uploaded
    image_file = request.files.get('image_file')
    if image_file and image_file.filename != '':
        new_image_url = save_image(image_file)
        if new_image_url:
            product.image_url = new_image_url
    
    db.session.commit()
    flash('Product updated successfully')
    return redirect(url_for('admin.manage_inventory'))

# --- CRUD: DELETE (NEW) ---
@admin_bp.route('/admin/product/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Optional: Delete image file from server to save space
    # if product.image_url != 'images/products/default.jpg':
    #     full_path = os.path.join(current_app.root_path, 'static', product.image_url)
    #     if os.path.exists(full_path):
    #         os.remove(full_path)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully')
    return redirect(url_for('admin.manage_inventory'))