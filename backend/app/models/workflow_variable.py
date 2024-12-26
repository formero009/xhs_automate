from app.extensions import db
from datetime import datetime, timezone

class WorkflowVariable(db.Model):
    __tablename__ = 'workflow_variables'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    node_id = db.Column(db.String(255), nullable=False)
    class_type_id = db.Column(db.Integer, db.ForeignKey('variable_definitions.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # 关联关系
    workflow = db.relationship('Workflow', backref='variables')
    variable_definition = db.relationship('VariableDefinitions', backref='variables') 