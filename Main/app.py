import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt

# Create a Flask app
app = Flask(__name__, template_folder='Frontend')

# Set the secret key
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))  # Randomly generated key for dev

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)  # Store hashed password as binary
    is_admin = db.Column(db.Boolean, default=False)  # New column to define user type
    admin_request = db.Column(db.Boolean, default=False)  # Column for requesting admin privileges

    def __repr__(self):
        return f'<User {self.username} (Admin: {self.is_admin})>'

# Create the database and tables
with app.app_context():
    db.create_all()
    print("Database tables created!")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin_request = request.form.get('admin_request', False)

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user = User(username=username, password=hashed_password, admin_request=bool(admin_request))
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('user_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    users = User.query.filter_by(is_admin=False).all()
    admin_requests = User.query.filter_by(admin_request=True, is_admin=False).all()
    return render_template('admin_dashboard.html', users=users, admin_requests=admin_requests)

@app.route('/approve_admin/<int:user_id>')
def approve_admin(user_id):
    user = User.query.get(user_id)
    if user and not user.is_admin:
        user.is_admin = True
        user.admin_request = False
        db.session.commit()
        flash(f'User {user.username} is now an admin!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
