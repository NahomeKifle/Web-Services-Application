#Nahome Kifle
#Cart Service

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cart.sqlite')
db = SQLAlchemy(app)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  
    product_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    cart_list = [{"id": item.id, "name": item.name, "price": item.price, "quantity": item.quantity} for item in cart_items]
    return jsonify({"cart": cart_list})

@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_product(user_id, product_id):
    
    response = requests.get(f'http://127.0.0.1:5000/products/{product_id}')

    if response.status_code != 200:
        return jsonify({"error": "Product not found"}), 404
    
    product_data = response.json().get('product')
    
    if not product_data:
        return jsonify({"error": "Product not found"}), 404
    
    available_quantity = product_data['quantity']
    
   
    data = request.json
    quantity_to_add = data.get('quantity', 1)  
    
    if available_quantity < quantity_to_add:
        return jsonify({"error": "Insufficient quantity"}), 400

    
    existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if existing_cart_item:
        
        existing_cart_item.quantity += quantity_to_add
        db.session.commit()
    else:
        
        new_cart_item = Cart(user_id=user_id, product_id=product_id, name=product_data['name'], price=product_data['price'], quantity=quantity_to_add)
        db.session.add(new_cart_item)
        db.session.commit()

    
    updated_quantity = available_quantity - quantity_to_add
    requests.put(f'http://127.0.0.1:5000/products/{product_id}', json={"quantity": updated_quantity})

    return jsonify({"message": "Product added to cart", "product": product_data, "quantity_added": quantity_to_add}), 201

@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_product_quantity(user_id, product_id):
    data = request.get_json()
    quantity_to_remove = data.get('quantity', 1)  

    # Step 1: Find the product in the user's cart
    product_in_cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if not product_in_cart:
        return jsonify({"error": "Product is not in the cart"}), 404

    
    if product_in_cart.quantity < quantity_to_remove:
        return jsonify({"error": "Quantity to remove exceeds quantity in cart"}), 400

    product_in_cart.quantity -= quantity_to_remove

    if product_in_cart.quantity == 0:
        db.session.delete(product_in_cart)
    else:
        db.session.add(product_in_cart)

    response = requests.get(f'http://127.0.0.1:5000/products/{product_id}')
    if response.status_code != 200:
        return jsonify({"error": "Product not found in inventory"}), 404
    
    product_data = response.json().get('product')
    if not product_data:
        return jsonify({"error": "Product not found in inventory"}), 404

    updated_quantity = product_data['quantity'] + quantity_to_remove
    update_response = requests.put(f'http://127.0.0.1:5000/products/{product_id}', json={"quantity": updated_quantity})

    if update_response.status_code != 200:
        return jsonify({"error": "Failed to update product quantity"}), 500

    db.session.commit()

    message = f"Removed {quantity_to_remove} from the cart. Remaining quantity in cart: {product_in_cart.quantity}" if product_in_cart.quantity > 0 else "Product removed from the cart."
    
    return jsonify({"message": message, "updated_quantity_in_inventory": updated_quantity}), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True)