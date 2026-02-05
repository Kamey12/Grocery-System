from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role') 
        
  
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger') 
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))

        if role == 'admin':
            secret_code = request.form.get('admin_secret')
            
           
            if secret_code != 'admin123': 
                flash('Invalid Admin Secret Code! Registration failed.', 'danger')
                return redirect(url_for('auth.register'))

     
        if role not in ['customer', 'admin']:
            role = 'customer'

 
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role  
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        if role == 'admin':
            flash('Admin account created successfully!', 'success')
        else:
            flash('Registration successful! Welcome to Vegefoods.', 'success')
            
        return redirect(url_for('main.dashboard'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth_bp.route('/select-role', methods=['GET', 'POST'])
@login_required
def select_role():
    if current_user.role != 'pending':
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['customer', 'admin']:
            current_user.role = role
            db.session.commit()
            flash(f'Welcome! You are now registered as a {role}.')
            return redirect(url_for('main.dashboard'))
    return render_template('select_role.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('main.dashboard'))