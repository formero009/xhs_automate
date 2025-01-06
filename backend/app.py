import os
from app import create_app
from app.extensions import db
from conf import DATABASE_URI
from app.scheduler import scheduler

app = create_app()

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Initialize scheduler with app
scheduler.init_app(app)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)