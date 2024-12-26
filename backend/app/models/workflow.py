from datetime import datetime
from app.extensions import db

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_size = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)
    content_md5 = db.Column(db.String(32), unique=True)
    input_vars = db.Column(db.ARRAY(db.String))
    output_vars = db.Column(db.ARRAY(db.String))
    preview_image = db.Column(db.Text)
    
    @property
    def normalized_file_path(self):
        """返回规范化的文件路径（使用正斜杠）"""
        return self.file_path.replace('\\', '/') if self.file_path else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_name': self.original_name,
            'name': self.name,
            'file_path': self.normalized_file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'file_size': self.file_size,
            'status': self.status,
            'content_md5': self.content_md5,
            'input_vars': self.input_vars,
            'output_vars': self.output_vars,
            'preview_image': self.preview_image
        }
  

  