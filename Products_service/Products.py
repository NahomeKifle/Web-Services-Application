#Nahome Kifle
#Product Service

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.sqlite')
db = SQLAlchemy(app)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/products', methods=['GET'])
def get_products():
    products = Products.query.all()
    product_list = [{"id": product.id, "name": product.name, "price": product.price, "quantity": product.quantity} for product in products]
    return jsonify({"products": product_list})

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Products.query.get(product_id)
    if product:
        return jsonify({"product": {"id": product.id, "name": product.name, "price": product.price, "quantity": product.quantity}})
    else:
        return jsonify({"error": "Product not found"}), 404
    

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    if "price" not in data:
        return jsonify({"error": "Price is required"}), 400
    if "quantity" not in data:
        return jsonify({"error": "Quantity is required"}), 400
    
    new_product = Products(name=data['name'], price=data['price'], quantity=data['quantity'])
    
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product created", "product": {"id": new_product.id, "name": new_product.name, "price": new_product.price, "quantity": new_product.quantity}}), 201

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product_quantity(product_id):
    product = Products.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.json
    product.quantity = data.get('quantity', product.quantity)
    
    db.session.commit()
    return jsonify({"message": "Product quantity updated", "product": {"id": product.id, "name": product.name, "quantity": product.quantity}})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
