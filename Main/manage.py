from flask import Flask
from flask_migrate import Migrate
from app import db  # Change 'your_app_file' to the name of your app's main file (without .py extension)

app = Flask(__name__)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
