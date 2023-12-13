from src import db

class Environment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(10), unique=True, nullable=False)
    base_endpoint = db.Column(db.String(512), unique=False, nullable=False)
    client_id = db.Column(db.String(512), unique=True, nullable=False)
    client_secret = db.Column(db.String(512), unique=True, nullable=False)
    bearer_token = db.Column(db.String(512), unique=True, nullable=False)

