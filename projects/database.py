from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    request_count = db.Column(db.Integer, default=1)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
