from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import smtplib
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, ProductForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    products = db.relationship('Product', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def is_authenticated(self):
        return True  # Assume all users are authenticated

    @property
    def is_active(self):
        return True  # Assume all users are active

    @property
    def is_anonymous(self):
        return False  # Assume all users are not anonymous

    def get_id(self):
        return str(self.id)  # Convert the id to unicode to support Flask-Login's requirements


# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), nullable=False)
    product_link = db.Column(db.String(200), nullable=True)
    buy_price = db.Column(db.Float(precision=2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_price = db.Column(db.Float(precision=2), nullable=True, default=None)
    last_alert_sent = db.Column(db.DateTime(), nullable=True, default=None)

    def __repr__(self):
        return '<Product %r>' % self.product_name


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Username already exists.', 'danger')
        elif existing_email:
            flash('Email address already registered.', 'danger')
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('products'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template("login.html", form=form)


@app.route("/demo_login", methods=["GET", "POST"])
def demo_login():
    demo_email = 'thisisjustadummy@email.com'
    user = User.query.filter_by(email=demo_email).first()
    if user is not None:
        login_user(user)
        flash('Logged in as demo user', 'success')
        return redirect(url_for('products'))
    else:
        flash('Demo user not found', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/add_product', methods=["GET", "POST"])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        product_link = form.product_link.data
        buy_price = form.buy_price.data
        current_price = None
        if "amazon.com" not in product_link:
            flash('This is not an Amazon link. Please add a valid Amazon product link.', 'danger')
            return redirect(url_for('add_product'))
        else:
            product = Product(product_name=product_name, product_link=product_link,
                              buy_price=buy_price, user_id=current_user.id, current_price=current_price)
            db.session.add(product)
            db.session.commit()
            flash('Successfully added product.', 'success')
            return redirect(url_for('products'))
    products = Product.query.filter_by(user_id=current_user.id)
    return render_template("add_product.html", form=form, products=products)


@app.route('/delete_product/<int:product_id>', methods=["POST", "DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    flash('Successfully deleted product.', 'success')
    return redirect(url_for('products'))


@app.route('/products')
@login_required
def products():
    # Get all the products associated with the current user
    user_products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('products.html', products=user_products)


@app.route("/check_price/<int:product_id>")
@login_required
def check_price(product_id):
    # Get the current date and time
    now = datetime.now()
    date_string = now.strftime("%m-%d-%y")
    time_string = now.strftime("%H:%M")

    # Set the time delta for 30 minutes
    time_delta = timedelta(minutes=5)

    product = Product.query.filter_by(user_id=current_user.id, id=product_id).first()
    product_name = product.product_name
    buy_price = product.buy_price
    product_link = product.product_link
    count = 0
    email_sent = False
    while not email_sent:
        response = requests.get(product_link, headers={
            "User-Agent": "Defined",
            "Accept-Language": "en-US,en;q=0.5"
            }).text
        # Scrape the amazon product page for the price using beautiful soup
        soup = BeautifulSoup(response, "html.parser")
        price_whole = soup.find(name="span", class_="a-price-whole")
        price_fraction = soup.find(name="span", class_="a-price-fraction")
        if price_whole is not None and price_fraction is not None:
            product.current_price = float(price_whole.getText() + price_fraction.getText())
            current_price = product.current_price
            db.session.commit()
            if current_price < buy_price and (product.last_alert_sent is None or product.last_alert_sent + time_delta <= now):
                message = f"{product_name} is now at or below ${buy_price:.2f} as of {date_string} {time_string}."
                with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                    connection.starttls()
                    result = connection.login(user=my_email, password=password)
                    connection.sendmail(
                        from_addr=my_email,
                        to_addrs=current_user.email,
                        msg=f"Subject:Amazon Price Alert!\n\n{message}\n\nBuy now below!\n{product_link}"
                    )
                product.last_alert_sent = datetime.strptime(now.strftime('%m-%d-%y %H:%M:%S'), '%m-%d-%y %H:%M:%S')
                db.session.commit()
                flash(f"Email has been sent for {product_name} on {date_string} at {time_string}.", "success")
                email_sent = True
                break
            break
        count += 1
        flash(f"Attempt #{count}. Price not found. Retrying in 5 seconds...", 'danger')
        time.sleep(5)
        if count > 3:
            flash(f"Unable to check prices right now. Please try again later.", 'danger')
            return False
    if product is not None:
        current_price = product.current_price
        return jsonify({'current_price': current_price, 'date': date_string, 'time': time_string})
    else:
        return jsonify({'error': 'Product not found'})


if __name__ == '__main__':
    app.run(debug=True)


