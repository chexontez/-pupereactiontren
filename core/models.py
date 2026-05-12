from datetime import datetime
from core import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('TestResult', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class TestResult(db.Model):
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    average_reaction_time = db.Column(db.Float, nullable=False) # в миллисекундах
    min_reaction_time = db.Column(db.Float, nullable=False)
    max_reaction_time = db.Column(db.Float, nullable=False)
    correct_responses = db.Column(db.Integer, nullable=False)
    total_attempts = db.Column(db.Integer, nullable=False)
    false_responses = db.Column(db.Integer, nullable=False, default=0)
    previous_avg_comparison = db.Column(db.Float, nullable=True) # Разница с предыдущим тестом

    def __repr__(self):
        return f'<TestResult {self.id} for User {self.user_id}>'