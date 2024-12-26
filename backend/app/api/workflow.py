from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from app.extensions import db
from app.models.variable_definitions import VariableDefinitions
from datetime import datetime, timezone
from app.utils.response import success_response, error_response
from app.models.workflow_variable import WorkflowVariable
from app.models.workflow import Workflow
import hashlib
from app.utils.logger import logger
from typing import List, Optional
from sqlalchemy.orm import Session

from app.utils.util import get_json_value_with_type

bp = Blueprint('workflow', __name__, url_prefix='/api/workflow')

UPLOAD_FOLDER = 'upload/workflows'
ALLOWED_EXTENSIONS = {'json'}
MAX_CONTENT_LENGTH = 1024 * 1024  # 1024KB limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_workflow_json(workflow_data):
    """
    验证工作流JSON格式是否合法
    
    Args:
        workflow_data (dict): 解析后的工作流JSON数据
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(workflow_data, dict):
        return False, "Invalid workflow format: root must be an object"
    
    if not workflow_data:
        return False, "Invalid workflow format: workflow is empty"
    
    for node_id, node_data in workflow_data.items():
        # 验证节点ID是否为字符串类型
        if not isinstance(node_id, str):
            return False, f"Invalid node ID format: {node_id}, must be string"
        
        # 验证节点数据是否为字典类型
        if not isinstance(node_data, dict):
            return False, f"Invalid node data format for node {node_id}: must be an object"
        
        # 验证必需字段
        required_fields = ['inputs', 'class_type', '_meta']
        for field in required_fields:
            if field not in node_data:
                return False, f"Missing required field '{field}' in node {node_id}"
        
        # 验证inputs是否为字典
        if not isinstance(node_data['inputs'], dict):
            return False, f"Invalid inputs format in node {node_id}: must be an object"
        
        # 验证class_type是否为字符串
        if not isinstance(node_data['class_type'], str):
            return False, f"Invalid class_type format in node {node_id}: must be string"
        
        # 验证_meta是否为字典包含title字段
        if not isinstance(node_data['_meta'], dict):
            return False, f"Invalid _meta format in node {node_id}: must be an object"
        
        if 'title' not in node_data['_meta']:
            return False, f"Missing title in _meta for node {node_id}"
        
        if not isinstance(node_data['_meta']['title'], str):
            return False, f"Invalid title format in node {node_id}: must be string"
    
    return True, ""

def parse_workflow_variables(workflow_json: dict, db: Session, workflow_id: int):
    """解析工作流变量并保存到数据库"""
    for node_id, node_data in workflow_json.items():
        class_type = node_data.get("class_type")
        if not class_type:
            continue
            
        # 检查是否已存在该类型的定义
        definitions = VariableDefinitions.query.filter_by(class_type=class_type).all()
        for definition in definitions:
            should_create_variable = False
            
            if definition.param_type == 'input':
                # 对于输入类型，需要验证value_path和value_type
                value, actual_type = get_json_value_with_type(node_data, definition.value_path)
                if value is not None and actual_type == definition.value_type.lower():
                    should_create_variable = True
                else:
                    logger.debug(f"Skip input variable definition: path={definition.value_path}, "
                               f"expected_type={definition.value_type}, actual_type={actual_type}")
            else:
                # 对于输出类型，直接创建变量记录
                should_create_variable = True
            
            if should_create_variable:
                variable = WorkflowVariable(
                    workflow_id=workflow_id,
                    node_id=node_id,
                    class_type_id=definition.id,
                    title=node_data['_meta']['title']
                )
                logger.info(f"创建变量记录: workflow_id={workflow_id}, node_id={node_id}, "
                          f"class_type={class_type}, value_path={definition.value_path}, "
                          f"param_type={definition.param_type}")
                db.session.add(variable)
    
    db.session.commit()

@bp.route('/upload', methods=['POST'])
def upload_workflow():
    try:
        logger.info("Starting workflow upload")
        
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return error_response('No file part')
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("No selected file")
            return error_response('No selected file')

        # 检查文件类型
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return error_response('Invalid file type. Only JSON files are allowed')

        logger.info(f"Processing file: {file.filename}")
        
        # 检查文件大小
        file_content = file.read()
        if len(file_content) > MAX_CONTENT_LENGTH:
            logger.warning(f"File size exceeds limit: {len(file_content)} bytes")
            return error_response(f'File size exceeds {MAX_CONTENT_LENGTH/1024}KB limit')
        
        # 计算文件内容的MD5值
        content_md5 = hashlib.md5(file_content).hexdigest()
        logger.info(f"File MD5: {content_md5}")
        
        # 检查是否存在相同内容的工作流
        existing_workflow = Workflow.query.filter_by(content_md5=content_md5).first()
        if existing_workflow:
            logger.info(f"Found existing workflow with same content: {existing_workflow.id}")
            return success_response(
                message='Workflow already exists',
                data={
                    'id': existing_workflow.id,
                    'original_name': existing_workflow.original_name,
                    'name': existing_workflow.name,
                    'file_size': existing_workflow.file_size,
                    'created_at': existing_workflow.created_at.isoformat(),
                    'variables_count': len(existing_workflow.variables)
                }
            )
        
        file.seek(0)  # 重置文件指针
        
        # 生成唯一文件名（用于存储）
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        original_filename = file.filename
        safe_filename = secure_filename(original_filename)
        storage_filename = f"{os.path.splitext(safe_filename)[0]}_{timestamp}.json"
        file_path = os.path.join(UPLOAD_FOLDER, storage_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 在保存工作流时规范化路径
        file_path = file_path.replace('\\', '/')
        
        try:
            # 解析JSON内容
            workflow_data = json.loads(file_content.decode('utf-8'))
            
            # 验证工作流格式
            is_valid, error_message = validate_workflow_json(workflow_data)
            if not is_valid:
                raise ValueError(f"Invalid workflow format: {error_message}")
            
            # 创建工作流记录
            workflow = Workflow(
                original_name=original_filename,
                name=storage_filename,
                file_path=file_path,
                file_size=len(file_content),
                content_md5=content_md5,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.session.add(workflow)
            db.session.flush()
            
            # 解析并保存工作流变量
            parse_workflow_variables(workflow_data, db, workflow.id)
            
            db.session.commit()
            
            logger.info(f"Successfully created workflow: {workflow.id}")
            return success_response(
                message='Workflow uploaded successfully',
                data={
                    'id': workflow.id,
                    'original_name': original_filename,
                    'name': workflow.name,
                    'file_size': workflow.file_size,
                    'created_at': workflow.created_at.isoformat(),
                    'variables_count': len(workflow_data)
                }
            )
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
            
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            logger.info(f"Removing invalid workflow file: {file_path}")
            os.remove(file_path)
        return error_response(str(e))
        
    except Exception as e:
        logger.exception("Unexpected error during workflow upload")
        if 'file_path' in locals() and os.path.exists(file_path):
            logger.info(f"Removing workflow file due to error: {file_path}")
            os.remove(file_path)
        return error_response(f"An unexpected error occurred: {str(e)}")

@bp.route('/list', methods=['GET'])
def list_workflows():
    try:
        logger.info("Starting workflow list request")
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        logger.info(f"List params - page: {page}, per_page: {per_page}, search: {search}")
        
        if per_page > 100:
            logger.warning(f"Requested per_page ({per_page}) exceeds limit, setting to 100")
            per_page = 100
            
        query = Workflow.query
        
        if search:
            query = query.filter(Workflow.original_name.ilike(f'%{search}%'))
            logger.info(f"Applying search filter: {search}")
            
        query = query.order_by(Workflow.status.desc(), Workflow.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page)
        logger.info(f"Found {pagination.total} total workflows")
        
        workflows = [{
            'id': workflow.id,
            'original_name': workflow.original_name,
            'file_size': workflow.file_size,
            'status': workflow.status,
            'created_at': workflow.created_at.isoformat(),
            'updated_at': workflow.updated_at.isoformat(),
            'variables_count': len(workflow.variables),
            'input_vars': json.loads(workflow.input_vars) if workflow.input_vars else [],
            'output_vars': json.loads(workflow.output_vars) if workflow.output_vars else [],
            'preview_image': workflow.preview_image
        } for workflow in pagination.items]
        
        logger.info(f"Successfully retrieved {len(workflows)} workflows")
        return success_response(
            message='Workflows retrieved successfully',
            data={
                'workflows': workflows,
                'pagination': {
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        )
        
    except Exception as e:
        logger.exception("Error while retrieving workflow list")
        return error_response(f"An error occurred while retrieving workflows: {str(e)}")

@bp.route('/<int:workflow_id>/toggle-status', methods=['POST'])
def toggle_workflow_status(workflow_id):
    try:
        logger.info(f"Toggling status for workflow {workflow_id}")
        
        workflow = Workflow.query.get_or_404(workflow_id)
        old_status = workflow.status
        
        workflow.status = not workflow.status
        workflow.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        logger.info(f"Successfully toggled workflow {workflow_id} status from {old_status} to {workflow.status}")
        return success_response(
            message=f"Workflow {'enabled' if workflow.status else 'disabled'} successfully",
            data={
                'id': workflow.id,
                'status': workflow.status
            }
        )
        
    except Exception as e:
        logger.exception(f"Error while toggling workflow {workflow_id} status")
        return error_response(f"An error occurred while toggling workflow status: {str(e)}")

@bp.route('/<int:workflow_id>/variables', methods=['GET'])
def get_workflow_variables(workflow_id):
    try:
        logger.info(f"Retrieving variables for workflow {workflow_id}")
        
        # Get param_type filter from query parameters
        param_type = request.args.get('param_type')  # 'input', 'output', or None for all
        
        workflow = Workflow.query.get_or_404(workflow_id)
        
        # Base query
        query = (WorkflowVariable.query
            .join(VariableDefinitions)
            .filter(WorkflowVariable.workflow_id == workflow_id))
        
        # Apply param_type filter if specified
        if param_type in ['input', 'output']:
            query = query.filter(VariableDefinitions.param_type == param_type)
            
        variables = query.order_by(WorkflowVariable.node_id).all()
        
        logger.info(f"Found {len(variables)} variables for workflow {workflow_id}")
        return success_response(
            message='Workflow variables retrieved successfully',
            data={
                'workflow': {
                    'id': workflow.id,
                    'originalName': workflow.original_name,
                    'status': workflow.status,
                    'input_vars': json.loads(workflow.input_vars) if workflow.input_vars else [],
                    'output_vars': json.loads(workflow.output_vars) if workflow.output_vars else [],
                    'preview_image': workflow.preview_image
                },
                'variables': [{
                    'id': variable.id,
                    'node_id': variable.node_id,
                    'class_type': variable.variable_definition.class_type,
                    'value_path': variable.variable_definition.value_path,
                    'value_type': variable.variable_definition.value_type,
                    'param_type': variable.variable_definition.param_type,
                    'title': variable.title,
                    'description': variable.variable_definition.description,
                    'created_at': variable.created_at.isoformat()
                } for variable in variables]
            }
        )
        
    except Exception as e:
        logger.exception(f"Error while retrieving variables for workflow {workflow_id}")
        return error_response(f"An error occurred while retrieving workflow variables: {str(e)}")

@bp.route('/<int:workflow_id>/update-vars', methods=['POST'])
def update_workflow_vars(workflow_id):
    try:
        logger.info(f"Updating input/output variables for workflow {workflow_id}")
        
        workflow = Workflow.query.get_or_404(workflow_id)
        data = request.get_json()
        
        # 验证请求数据
        input_vars = data.get('input_vars', [])
        output_vars = data.get('output_vars', [])
        preview_image = data.get('preview_image')  # 获取预览图路径
        
        if not isinstance(input_vars, list) or not isinstance(output_vars, list):
            return error_response("input_vars and output_vars must be arrays")
        # 验证所有供的node_id是否存在于该工作流的变量中
        workflow_vars = {var.id for var in workflow.variables}
       
        for node_id in input_vars + output_vars:
            if not isinstance(node_id, int):
                return error_response(f"Invalid node_id int format: {node_id}")
            if node_id not in workflow_vars:
                return error_response(f"Node ID not found in workflow: {node_id}")
        
        # ��列表序列化为JSON字符串后存储
        workflow.input_vars = json.dumps(input_vars)
        workflow.output_vars = json.dumps(output_vars)
        workflow.preview_image = preview_image  # 保存预览图路径
        workflow.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        logger.info(f"Successfully updated vars for workflow {workflow_id}")
        return success_response(
            message='Workflow variables updated successfully',
            data={
                'id': workflow.id,
                'input_vars': input_vars,
                'output_vars': output_vars,
                'preview_image': preview_image
            }
        )
        
    except Exception as e:
        logger.exception(f"Error while updating workflow {workflow_id} variables")
        return error_response(f"An error occurred while updating workflow variables: {str(e)}")