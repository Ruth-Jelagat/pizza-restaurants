from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)



@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([
        r.to_dict(only=('id', 'name', 'address'))
        for r in restaurants
    ]), 200


@app.route('/restaurants/<int:id>')
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    return jsonify(
        restaurant.to_dict(
            include={
                'restaurant_pizzas': {
                    'include': {
                        'pizza': {}
                    }
                }
            }
        )
    ), 200


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()

    return '', 204



@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([
        p.to_dict(only=('id', 'name', 'ingredients'))
        for p in pizzas
    ]), 200


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            restaurant_id=data['restaurant_id'],
            pizza_id=data['pizza_id']
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(
            restaurant_pizza.to_dict(
                include={
                    'restaurant': {},
                    'pizza': {}
                }
            )
        ), 201

    except Exception as e:
        return jsonify({
            "errors": [str(e)]
        }), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)

