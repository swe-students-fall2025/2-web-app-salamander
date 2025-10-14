from flask import Flask, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'job_trackr')

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Routes


@app.route('/')
def index():
    """Display all applications from the database"""
    applications = list(db.applications.find())
    return render_template('index.html', applications=applications)


if __name__ == '__main__':
    app.run(debug=True)
