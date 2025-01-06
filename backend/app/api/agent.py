from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.agent import Agent, AgentStatus, ScheduleType
from app.extensions import db
from app.scheduler import scheduler
from app.models.workflow import Workflow

bp = Blueprint('agent', __name__, url_prefix='/api/agent')

def validate_schedule_config(schedule_type, schedule_config):
    """验证调度配置是否有效"""
    if not isinstance(schedule_config, dict):
        return False, "调度配置必须是一个对象"
        
    if schedule_type == ScheduleType.FIXED_TIME:
        hour = schedule_config.get('hour')
        minute = schedule_config.get('minute', 0)
        if not isinstance(hour, int) or not (0 <= hour < 24):
            return False, "小时必须是0-23之间的整数"
        if not isinstance(minute, int) or not (0 <= minute < 60):
            return False, "分钟必须是0-59之间的整数"
            
    elif schedule_type == ScheduleType.TIMES_PER_DAY:
        times = schedule_config.get('times')
        if not isinstance(times, int) or times < 1 or times > 24:
            return False, "每天执行次数必须是1-24之间的整数"
            
    elif schedule_type == ScheduleType.DAYS_INTERVAL:
        days = schedule_config.get('days')
        hour = schedule_config.get('hour', 10)
        minute = schedule_config.get('minute', 0)
        if not isinstance(days, int) or days < 1:
            return False, "间隔天数必须是大于0的整数"
        if not isinstance(hour, int) or not (0 <= hour < 24):
            return False, "小时必须是0-23之间的整数"
        if not isinstance(minute, int) or not (0 <= minute < 60):
            return False, "分钟必须是0-59之间的整数"
            
    elif schedule_type == ScheduleType.WEEKLY:
        weekdays = schedule_config.get('weekdays')
        hour = schedule_config.get('hour', 10)
        minute = schedule_config.get('minute', 0)
        if not isinstance(weekdays, list) or not weekdays:
            return False, "必须指定至少一个星期几"
        if not all(isinstance(d, int) and 0 <= d < 7 for d in weekdays):
            return False, "星期几必须是0-6之间的整数（0=周一）"
        if not isinstance(hour, int) or not (0 <= hour < 24):
            return False, "小时必须是0-23之间的整数"
        if not isinstance(minute, int) or not (0 <= minute < 60):
            return False, "分钟必须是0-59之间的整数"
            
    return True, None

@bp.route('/agents', methods=['POST'])
def create_agent():
    data = request.get_json()
    
    # 验证必输字段
    required_fields = ['name', 'account_id', 'schedule_type', 'schedule_config', 'image_count']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'success': False,
            'message': f'缺少必填字段: {", ".join(missing_fields)}',
            'data': None
        }), 400
        
    # 验证字段值的合法性
    if not isinstance(data.get('image_count'), int) or not (1 <= data['image_count'] <= 9):
        return jsonify({
            'success': False,
            'message': '图片数量必须是1-9之间的整数',
            'data': None
        }), 400
        
    try:
        schedule_type = ScheduleType(data['schedule_type'])
    except ValueError:
        return jsonify({
            'success': False,
            'message': '无效的调度类型',
            'data': None
        }), 400
        
    # 验证调度配置
    is_valid, error_message = validate_schedule_config(schedule_type, data['schedule_config'])
    if not is_valid:
        return jsonify({
            'success': False,
            'message': error_message,
            'data': None
        }), 400

    # 验证workflow_id是否存在
    workflow_id = data.get('workflow_id')
    if workflow_id:
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return jsonify({
                'success': False,
                'message': '指定的工作流不存在',
                'data': None
            }), 400
    
    try:
        agent = Agent(
            name=data['name'],
            topic=data.get('topic', ''),
            account_id=data['account_id'],
            schedule_type=schedule_type,
            schedule_config=data['schedule_config'],
            image_count=data['image_count'],
            prompt_template=data.get('prompt_template'),
            image_style=data.get('image_style'),
            workflow_id=workflow_id,
            status=AgentStatus.PAUSED
        )
        db.session.add(agent)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '托管创建成功',
            'data': agent.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 400

@bp.route('/agents', methods=['GET'])
def list_agents():
    try:
        agents = Agent.query.all()
        return jsonify({
            'success': True,
            'message': '托管列表获取成功',
            'data': [agent.to_dict() for agent in agents]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 400

@bp.route('/agents/<int:agent_id>/toggle', methods=['PUT'])
def toggle_agent(agent_id):
    try:
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({
                'success': False,
                'message': '托管不存在',
                'data': None
            }), 404
        
        agent.status = AgentStatus.RUNNING if agent.status == AgentStatus.PAUSED else AgentStatus.PAUSED
        agent.updated_at = datetime.utcnow()
        
        if agent.status == AgentStatus.RUNNING:
            scheduler.schedule_agent(agent)
        else:
            scheduler.remove_agent(agent.id)
            agent.next_run = None
            
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '托管状态更新成功',
            'data': agent.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 400

@bp.route('/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    try:
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({
                'success': False,
                'message': '托管不存在',
                'data': None
            }), 404
        
        scheduler.remove_agent(agent.id)
        db.session.delete(agent)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Agent deleted successfully',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 400

@bp.route('/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    data = request.get_json()
    try:
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({
                'success': False,
                'message': 'Agent not found',
                'data': None
            }), 404

        # 验证必输字段
        required_fields = ['name', 'account_id', 'schedule_type', 'schedule_config', 'image_count']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'缺少必填字段: {", ".join(missing_fields)}',
                'data': None
            }), 400
            
        # 验证字段值的合法性
        if not isinstance(data.get('image_count'), int) or not (1 <= data['image_count'] <= 9):
            return jsonify({
                'success': False,
                'message': '图片数量必须是1-9之间的整数',
                'data': None
            }), 400
            
        try:
            schedule_type = ScheduleType(data['schedule_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的调度类型',
                'data': None
            }), 400
            
        # 验证调度配置
        is_valid, error_message = validate_schedule_config(schedule_type, data['schedule_config'])
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message,
                'data': None
            }), 400

        # 验证workflow_id是否存在
        workflow_id = data.get('workflow_id')
        if workflow_id:
            workflow = Workflow.query.get(workflow_id)
            if not workflow:
                return jsonify({
                    'success': False,
                    'message': '指定的工作流不存在',
                    'data': None
                }), 400

        # 更新字段
        agent.name = data['name']
        agent.topic = data.get('topic', '')
        agent.account_id = data['account_id']
        agent.schedule_type = schedule_type
        agent.schedule_config = data['schedule_config']
        agent.image_count = data['image_count']
        agent.prompt_template = data.get('prompt_template')
        agent.image_style = data.get('image_style')
        agent.workflow_id = workflow_id
        agent.updated_at = datetime.utcnow()

        # 如果 agent 正在运行，需要重新调度
        if agent.status == AgentStatus.RUNNING:
            scheduler.remove_agent(agent.id)
            scheduler.schedule_agent(agent)

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Agent updated successfully',
            'data': agent.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 400 