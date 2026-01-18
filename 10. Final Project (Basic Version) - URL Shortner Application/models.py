from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False, unique=True)
    short_code = db.Column(db.String(10), nullable=False, unique=True)
    clicks = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<URL {self.short_code}>"
