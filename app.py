

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- DATABASE TABLES ---------------- #

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))


class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    area = db.Column(db.String(100))
    phone = db.Column(db.String(20))


class FoodPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer)
    ngo_id = db.Column(db.Integer, nullable=True)  # NEW
    food_type = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    pickup_time = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Available")


with app.app_context():
    db.create_all()

# ---------------- HOME ---------------- #

@app.route('/')
def home():
    return render_template('home.html')


# ---------------- HOTEL REGISTER ---------------- #

@app.route('/hotel_register', methods=['GET', 'POST'])
def hotel_register():
    if request.method == 'POST':
        hotel = Hotel(
            name=request.form['name'],
            address=request.form['address'],
            phone=request.form['phone']
        )
        db.session.add(hotel)
        db.session.commit()
        return redirect(url_for('hotel_dashboard', hotel_id=hotel.id))
    return render_template('hotel_register.html')


# ---------------- NGO REGISTER ---------------- #

@app.route('/ngo_register', methods=['GET', 'POST'])
def ngo_register():
    if request.method == 'POST':
        ngo = NGO(
            name=request.form['name'],
            area=request.form['area'],
            phone=request.form['phone']
        )
        db.session.add(ngo)
        db.session.commit()
        return redirect(url_for('ngo_dashboard', ngo_id=ngo.id))
    return render_template('ngo_register.html')


# ---------------- POST FOOD ---------------- #

@app.route('/post_food/<int:hotel_id>', methods=['GET', 'POST'])
def post_food(hotel_id):
    if request.method == 'POST':
        post = FoodPost(
            hotel_id=hotel_id,
            food_type=request.form['food_type'],
            quantity=request.form['quantity'],
            pickup_time=request.form['pickup_time']
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('hotel_dashboard', hotel_id=hotel_id))
    return render_template('post_food.html', hotel_id=hotel_id)


# ---------------- HOTEL DASHBOARD ---------------- #

@app.route('/hotel_dashboard/<int:hotel_id>')
def hotel_dashboard(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    food_posts = FoodPost.query.filter_by(hotel_id=hotel_id).all()
    ngos = {ngo.id: ngo.name for ngo in NGO.query.all()}
    return render_template('hotel_dashboard.html',
                           hotel=hotel,
                           food_posts=food_posts,
                           ngos=ngos)


# ---------------- NGO DASHBOARD ---------------- #

@app.route('/ngo_dashboard/<int:ngo_id>')
def ngo_dashboard(ngo_id):
    available_food = FoodPost.query.filter_by(status="Available").all()
    claimed_food = FoodPost.query.filter_by(ngo_id=ngo_id).all()
    return render_template('ngo_dashboard.html',
                           available_food=available_food,
                           claimed_food=claimed_food,
                           ngo_id=ngo_id)


# ---------------- CLAIM FOOD ---------------- #

@app.route('/claim/<int:food_id>/<int:ngo_id>')
def claim_food(food_id, ngo_id):
    post = FoodPost.query.get(food_id)
    if post and post.status == "Available":
        post.status = "Claimed"
        post.ngo_id = ngo_id
        db.session.commit()
    return redirect(url_for('ngo_dashboard', ngo_id=ngo_id))


# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True, port=5001)
