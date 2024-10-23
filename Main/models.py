from db import db  # Import the db instance
from sqlalchemy import Column, Integer, String, Boolean

class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(db.LargeBinary, nullable=False)  # Store hashed password as binary
    is_admin = Column(Boolean, default=False)  # New column to define user type
    admin_request = Column(Boolean, default=False)  # Column for requesting admin privileges

    def __repr__(self):
        return f'<User {self.username} (Admin: {self.is_admin})>'
