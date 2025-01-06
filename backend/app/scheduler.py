from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.models.agent import Agent, AgentStatus, ScheduleType
from app.extensions import db
from xhs_upload.auto_upload import auto_gen_and_upload
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class AgentScheduler:
    _instance = None

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.scheduler = BackgroundScheduler()
            self.scheduler.start()
            self.job_map = {}  # agent_id -> job_id
            self.app = None
            self.initialized = True

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init_app(self, app):
        self.app = app
        # 在这里可以添加其他初始化逻辑
        with app.app_context():
            self.init_schedules()

    def calculate_next_run(self, schedule_type: ScheduleType, schedule_config: dict) -> datetime:
        now = datetime.utcnow()
        
        if schedule_type == ScheduleType.FIXED_TIME:
            # 计算下一个固定时间点
            hour = schedule_config.get('hour', 10)
            minute = schedule_config.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
            
        elif schedule_type == ScheduleType.TIMES_PER_DAY:
            # 计算一天内的下一个时间点
            times_per_day = schedule_config.get('times', 1)
            if times_per_day <= 0:
                times_per_day = 1
            interval_hours = 24 // times_per_day
            current_slot = now.hour // interval_hours
            next_slot_hour = (current_slot + 1) * interval_hours
            if next_slot_hour >= 24:
                next_slot_hour = 0
                next_run = now + timedelta(days=1)
            else:
                next_run = now
            return next_run.replace(hour=next_slot_hour, minute=0, second=0, microsecond=0)
            
        elif schedule_type == ScheduleType.DAYS_INTERVAL:
            # 计算N天后的时间点
            days = schedule_config.get('days', 1)
            hour = schedule_config.get('hour', 10)
            minute = schedule_config.get('minute', 0)
            if days <= 0:
                days = 1
            next_run = now + timedelta(days=days)
            return next_run.replace(hour=hour, minute=minute)
            
        elif schedule_type == ScheduleType.WEEKLY:
            # 计算下一个周几的时间点
            weekdays = schedule_config.get('weekdays', [0])  # 0=周一
            hour = schedule_config.get('hour', 10)
            minute = schedule_config.get('minute', 0)
            
            # 确保weekdays有效
            if not weekdays:
                weekdays = [0]
            weekdays = sorted(list(set([d % 7 for d in weekdays])))
            
            # 计算下一个有效的周几
            current_weekday = now.weekday()
            next_weekday = None
            for weekday in weekdays:
                if weekday > current_weekday:
                    next_weekday = weekday
                    break
            if next_weekday is None:  # 本周没有了，取下周第一天
                next_weekday = weekdays[0]
                days_ahead = 7 - current_weekday + next_weekday
            else:
                days_ahead = next_weekday - current_weekday
                
            next_run = now + timedelta(days=days_ahead)
            return next_run.replace(hour=hour, minute=minute)
            
        return now + timedelta(days=1)

    def get_trigger(self, schedule_type: ScheduleType, schedule_config: dict):
        """根据调度类型和配置获取对应的触发器"""
        if schedule_type == ScheduleType.FIXED_TIME:
            return CronTrigger(
                hour=schedule_config.get('hour', 10),
                minute=schedule_config.get('minute', 0)
            )
            
        elif schedule_type == ScheduleType.TIMES_PER_DAY:
            times_per_day = schedule_config.get('times', 1)
            if times_per_day <= 0:
                times_per_day = 1
            interval_hours = 24 // times_per_day
            return IntervalTrigger(hours=interval_hours)
            
        elif schedule_type == ScheduleType.DAYS_INTERVAL:
            days = schedule_config.get('days', 1)
            if days <= 0:
                days = 1
            return CronTrigger(
                hour=schedule_config.get('hour', 10),
                minute=schedule_config.get('minute', 0),
                day_of_week='*/' + str(days)
            )
            
        elif schedule_type == ScheduleType.WEEKLY:
            weekdays = schedule_config.get('weekdays', [0])
            if not weekdays:
                weekdays = [0]
            weekdays = sorted(list(set([d % 7 for d in weekdays])))
            weekdays_str = ','.join(str(d) for d in weekdays)
            return CronTrigger(
                hour=schedule_config.get('hour', 10),
                minute=schedule_config.get('minute', 0),
                day_of_week=weekdays_str
            )
            
        # 默认每天执行一次
        return CronTrigger(hour=10)

    def execute_agent(self, agent_id: int):
        """执行agent的任务"""
        if not self.app:
            logger.error("Scheduler not properly initialized with Flask app")
            return

        with self.app.app_context():
            try:
                agent = Agent.query.get(agent_id)
                if not agent or agent.status != AgentStatus.RUNNING:
                    return

                # 更新上次运行时间和下次运行时间
                agent.last_run = datetime.utcnow()
                agent.next_run = self.calculate_next_run(agent.schedule_type, agent.schedule_config)
                db.session.commit()

                # 执行Agent任务
                auto_gen_and_upload(
                    topic=agent.topic,
                    image_count=agent.image_count,
                    prompt_template=agent.prompt_template,
                    image_style=agent.image_style,
                    account_id=agent.account_id,
                    workflow_id=agent.workflow_id
                )
                
                logger.info(f"Agent {agent_id} executed successfully")
                
            except Exception as e:
                logger.error(f"Error executing agent {agent_id}: {str(e)}")
                try:
                    agent = Agent.query.get(agent_id)
                    if agent:
                        agent.status = AgentStatus.ERROR
                        db.session.commit()
                except Exception as inner_e:
                    logger.error(f"Error updating agent status: {str(inner_e)}")

    def schedule_agent(self, agent: Agent):
        """为agent添加调度任务"""
        if agent.id in self.job_map:
            self.remove_agent(agent.id)
            
        trigger = self.get_trigger(agent.schedule_type, agent.schedule_config)
        job = self.scheduler.add_job(
            func=self.execute_agent,
            trigger=trigger,
            args=[agent.id],
            id=f'agent_{agent.id}'
        )
        
        self.job_map[agent.id] = job.id
        agent.next_run = job.next_run_time
        db.session.commit()
        
        logger.info(f"Scheduled agent {agent.id} with next run at {agent.next_run}")

    def remove_agent(self, agent_id: int):
        """移除agent的调度任务"""
        if agent_id in self.job_map:
            try:
                self.scheduler.remove_job(self.job_map[agent_id])
                del self.job_map[agent_id]
                logger.info(f"Removed schedule for agent {agent_id}")
            except Exception as e:
                logger.error(f"Error removing agent {agent_id} schedule: {str(e)}")

    def init_schedules(self):
        """初始化所有运行状态的agent的调度任务"""
        if not self.app:
            logger.error("Cannot initialize schedules without Flask app")
            return

        with self.app.app_context():
            running_agents = Agent.query.filter_by(status=AgentStatus.RUNNING).all()
            for agent in running_agents:
                self.schedule_agent(agent)

# Create a global instance
scheduler = AgentScheduler.get_instance() 