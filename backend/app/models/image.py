from datetime import datetime
from app.extensions import db

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    workflow_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=False)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'))
    variables = db.Column(db.JSON)
    
    # 修改关系定义，指定正确的表名
    workflow = db.relationship('Workflow', 
                             backref=db.backref('images', lazy=True),
                             foreign_keys=[workflow_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'workflow_name': self.workflow_name,
            'workflow_id': self.workflow_id,
            'created_at': self.created_at.isoformat(),
            'file_path': self.file_path,
            'variables': self.variables
        } 