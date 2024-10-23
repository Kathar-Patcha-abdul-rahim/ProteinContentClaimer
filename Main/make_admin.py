from flask import Flask
from models import db, User
import bcrypt

# Create a Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Create an admin user within the app context
def create_admin_user():
    with app.app_context():
        db.create_all()  # Ensure tables are created

        # Define admin user details
        admin_username = 'kathar-patcha'
        admin_password = 'internship-sem3'

        # Check if the admin user already exists
        existing_admin = User.query.filter_by(username=admin_username).first()
        if existing_admin:
            print(f"User {admin_username} already exists!")
        else:
            # Hash the password
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

            # Create a new admin user
            new_admin = User(username=admin_username, password=hashed_password, is_admin=True)

            # Add and commit the new user to the database
            db.session.add(new_admin)
            db.session.commit()

            print(f"Admin user {admin_username} added successfully!")

if __name__ == '__main__':
    create_admin_user()
