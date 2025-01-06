from enum import Enum
from datetime import datetime
from app.extensions import db

class AgentStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class ScheduleType(str, Enum):
    FIXED_TIME = "fixed_time"  # 固定时间，每天执行一次
    TIMES_PER_DAY = "times_per_day"  # 每天执行N次
    DAYS_INTERVAL = "days_interval"  # 每N天执行一次
    WEEKLY = "weekly"  # 每周指定天执行

class Agent(db.Model):
    __tablename__ = 'agents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.Text, nullable=False)
    account_id = db.Column(db.String(50), nullable=False)
    
    # 调度相关字段
    schedule_type = db.Column(db.Enum(ScheduleType), nullable=False)
    schedule_config = db.Column(db.JSON, nullable=False)  # 存储具体的调度配置
    
    image_count = db.Column(db.Integer, nullable=False)
    prompt_template = db.Column(db.Text)
    image_style = db.Column(db.Text)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=True)
    status = db.Column(db.Enum(AgentStatus), default=AgentStatus.PAUSED)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship
    workflow = db.relationship('Workflow', backref='agents')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'topic': self.topic,
            'account_id': self.account_id,
            'schedule_type': self.schedule_type.value,
            'schedule_config': self.schedule_config,
            'image_count': self.image_count,
            'prompt_template': self.prompt_template,
            'image_style': self.image_style,
            'workflow_id': self.workflow_id,
            'status': self.status.value if self.status else None,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 