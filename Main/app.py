import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt

from Main.Backend import inputExtraction, loadData
from Main.Backend.calculation import process_enhanced_data, perform_operation, display_results
from Main.Backend.logic import process_data, perform

# Create a Flask app
app = Flask(__name__, template_folder='Frontend')

# Set the secret key
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))  # Randomly generated key for dev

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure you have a directory to save uploaded files
UPLOAD_FOLDER = 'Main/resources'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route('/process_manual', methods=['POST'])
def process_manual():
    # Retrieve values from manual input form
    name = request.form.get('name')
    pdcaas = float(request.form.get('pdcaas'))  # Make sure the form has 'pdcaas'
    protein_percentage = float(request.form.get('protein_percentage'))
    ivpdcaas = float(request.form.get('ivpdcaas'))

    # Convert values if necessary
    #protein = convert_if_percentage(protein_percentage)

    # Prepare the input data in a similar format as the Excel data
    input = [{
        'sample': name,
        'protein': protein_percentage,
        'pdcaas': pdcaas,
        'ivpdcaas': ivpdcaas
    }]

    data_file = loadData.main("resources/NutritionReferenceAmounts.json")
    enhanced_data = process_data(input, data_file)
    results = process_enhanced_data(enhanced_data)

    #results['pdcaas-claim']

    # Redirect or render the results page
    return render_template('results.html', results=results)  # Modify this as needed

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    # Handle Excel file upload
    if 'excel_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['excel_file']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        # Save the file locally
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        json_path = "resources/NutritionReferenceAmounts.json"

        # Process the data
        enhanced_data = perform_operation(file_path, json_path)

        # Render the results
        return render_template('results.html', results=enhanced_data)

    flash('Invalid file format. Please upload an Excel file.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        # Handle adding a new user from the admin dashboard
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
            flash('User added successfully!', 'success')

    # Fetch all users and admin requests
    users = User.query.all()
    admin_requests = User.query.filter_by(admin_request=True, is_admin=False).all()
    return render_template('admin_dashboard.html', users=users, admin_requests=admin_requests)

@app.route('/approve_admin/<int:user_id>')
def approve_admin(user_id):
    user = User.query.get(user_id)
    if user and not user.is_admin:
        user.is_admin = True  # Grant admin rights
        user.admin_request = False  # Reset the admin request flag
        db.session.commit()
        flash(f'User {user.username} is now an admin!', 'success')
    else:
        flash('Invalid user or user is already an admin.', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/disapprove_admin/<int:user_id>')
def disapprove_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.admin_request = False
        db.session.commit()
        flash(f'Admin request for {user.username} has been disapproved.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    # Handle logout logic (e.g., clearing the session)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
