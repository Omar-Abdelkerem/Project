from datetime import datetime
from app import db

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, nullable=False)
    delivery_agent_id = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), default="Pending")

    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    out_for_delivery_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    failed_at = db.Column(db.DateTime)
