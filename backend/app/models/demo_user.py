from app.extensions import db
from app.models.base import BaseModel


class DemoUser(BaseModel):
    __tablename__ = "demo_user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
