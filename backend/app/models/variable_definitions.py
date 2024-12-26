from app.extensions import db
from datetime import datetime, timezone

class VariableDefinitions(db.Model):
    __tablename__ = 'variable_definitions'
    
    id = db.Column(db.Integer, primary_key=True)
    class_type = db.Column(db.String(255), nullable=False)
    value_path = db.Column(db.String(255), nullable=False)
    value_type = db.Column(db.String(50), nullable=False)
    param_type = db.Column(db.String(10), nullable=False)  # 'input' or 'output'
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))