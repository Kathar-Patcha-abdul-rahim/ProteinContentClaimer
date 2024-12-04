import os
import time

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt
import pandas as pd
from io import BytesIO
from flask import send_file

from Main.Backend import inputExtraction, loadData
from Main.Backend.calculation import process_enhanced_data, perform_operation, display_results
from Main.Backend.logic import process_data, perform
from flask_socketio import SocketIO, send



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

# Initialize Flask-SocketIO for real-time chat
socketio = SocketIO(app)

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
            session['username'] = user.username  # Store the username in session
            session.permanent = True  # Make the session permanent
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
    global df
    # Handle Excel file upload
    if 'excel_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['excel_file']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        # Save the file temporarily to process
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        json_path = "resources/NutritionReferenceAmounts.json"

        # Process the data and add new fields
        enhanced_data = perform_operation(file_path, json_path)

        # Load the original Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)

        # Add new columns based on enhanced data
        df['PDCAAS'] = [entry['pdcaas'] for entry in enhanced_data]
        df['PDCAAS Claim'] = [entry['pdcaas_claim'] for entry in enhanced_data]
        df['PDCAAS Claim Status'] = [entry['pdcaas_claim_status'] for entry in enhanced_data]
        df['IVPDCAAS'] = [entry['ivpdcaas'] for entry in enhanced_data]
        df['IVPDCAAS Claim'] = [entry['ivpdcaas_claim'] for entry in enhanced_data]
        df['IVPDCAAS Claim Status'] = [entry['ivpdcaas_claim_status'] for entry in enhanced_data]

        # Save the updated DataFrame to an in-memory file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # Render results page with download option
        return render_template('results.html', results=enhanced_data, download_file=True)

    flash('Invalid file format. Please upload an Excel file.', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/download_excel')
def download_excel():
    global df  # Ensure the global df is referenced
    if df.empty:
        flash('No data available for download. Please upload and process an Excel file first.', 'danger')
        return redirect(url_for('dashboard'))

    # Create an in-memory file with the updated data
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    # Send the file as a download response
    return send_file(output, download_name='updated_data.xlsx', as_attachment=True)


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
    # Clear the session to log the user out
    session.clear()
    # Flash a message to confirm logout
    flash('You have been logged out.', 'success')
    # Redirect to the home page (or login page)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

# Global chat
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@socketio.on('message')
def handle_message(msg):
    username = session.get('username')  # Ensure the username is being retrieved from the session
    # Send both the username and the message to the frontend
    send({'username': username, 'message': msg}, broadcast=True)




# Running the app
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)


