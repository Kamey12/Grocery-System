from grocery_system import create_app, db
from grocery_system.models import User, Product
from werkzeug.security import generate_password_hash

app = create_app()

# Sample data updated to match your screenshot filenames
SAMPLE_PRODUCTS = [
    {
        'name': 'Fresh Apples',
        'description': 'Crisp and sweet apples.',
        'price': 2.99,
        'stock': 100,
        'category': 'Fruits',
        'image_url': 'images/products/apples.jpg'
    },
    {
        'name': 'Basmati Rice',
        'description': 'Premium long-grain aromatic rice.',
        'price': 12.99,
        'stock': 50,
        'category': 'Grains',
        'image_url': 'images/products/basmati_rice.jpg'
    },
    {
        'name': 'Whole Wheat Bread',
        'description': 'Freshly baked whole wheat bread.',
        'price': 3.49,
        'stock': 40,
        'category': 'Bakery',
        'image_url': 'images/products/bread.jpg'
    },
    {
        'name': 'Cheddar Cheese',
        'description': 'Sharp cheddar cheese block.',
        'price': 5.49,
        'stock': 60,
        'category': 'Dairy',
        'image_url': 'images/products/cheddar-cheese.jpg'
    },
    {
        'name': 'Fresh Carrots',
        'description': 'Organic crunchy carrots.',
        'price': 1.99,
        'stock': 150,
        'category': 'Vegetables',
        'image_url': 'images/products/carrots.jpg'
    },
    {
        'name': 'Chicken Breast',
        'description': 'Boneless skinless chicken breast.',
        'price': 8.99,
        'stock': 30,
        'category': 'Meat',
        'image_url': 'images/products/chicken.jpg'
    },
    {
        'name': 'Orange Juice',
        'description': 'Fresh squeezed orange juice.',
        'price': 5.99,
        'stock': 45,
        'category': 'Beverages',
        'image_url': 'images/products/orange-juice.jpg'
    },
    {
        'name': 'Nutella',
        'description': 'Hazelnut spread with cocoa.',
        'price': 4.99,
        'stock': 80,
        'category': 'Pantry',
        'image_url': 'images/products/nutella.jpg'
    },
    {
        'name': 'Greek Yogurt',
        'description': 'Creamy plain greek yogurt.',
        'price': 3.99,
        'stock': 25,
        'category': 'Dairy',
        'image_url': 'images/products/greek.jpg'
    }
]

if __name__ == '__main__':
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        
        # Create Admin if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            print("Admin user created.")
            
        # Seed Products if empty
        if Product.query.count() == 0:
            for product_data in SAMPLE_PRODUCTS:
                product = Product(**product_data)
                db.session.add(product)
            print("Sample products added.")
            
        db.session.commit()
            
    app.run(debug=True)