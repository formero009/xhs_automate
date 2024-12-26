from flask import Blueprint, request, send_from_directory
from app.utils.response import success_response, error_response
from werkzeug.utils import secure_filename
from conf import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, OUTPUT_FOLDER, BASE_PATH
import os
from pathlib import Path
from comfyui_api.utils.actions.prompt_to_image import prompt_to_image
from comfyui_api.utils.actions.load_workflow import load_workflow
from app.models.image import Image
from app.extensions import db
from app.utils.logger import logger
from app.models.workflow import Workflow
from app.models.variable_definitions import VariableDefinitions
from app.models.workflow_variable import WorkflowVariable

bp = Blueprint('image', __name__, url_prefix='/api')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        logger.info("Starting image upload request")
        
        if 'file' not in request.files:
            logger.warning("No file part in the request")
            return error_response('No file part in the request')
            
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("No file selected")
            return error_response('No file selected')
            
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return error_response(f'File type not allowed. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}')
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            logger.info(f"File {filename} already exists, trying {base}_{counter}{extension}")
            filename = f"{base}_{counter}{extension}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            counter += 1
            
        file.save(file_path)
        logger.info(f"Successfully saved file: {filename}")
        
        return success_response({
            'filename': filename,
            'path': f'/images/upload/{filename}'
        })
        
    except Exception as e:
        logger.exception("Error during image upload")
        return error_response('Upload failed', 500)


@bp.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        logger.info("Starting image generation request")
        
        data = request.json
        workflow_id = data.get('workflow_id')
        variables = data.get('variables', [])
        output_vars = data.get('output_vars', [])
        
        if not workflow_id:
            logger.warning("Missing workflow_id in request")
            return error_response('Missing required field: workflow_id')
            
        # 获取工作流信息
        workflow = Workflow.query.get_or_404(workflow_id)
        
        # 规范化路径处理
        normalized_path = workflow.file_path.replace('\\', '/')
        workflow_path = os.path.join(BASE_PATH, normalized_path)
        
        if not os.path.exists(workflow_path):
            logger.error(f"Workflow file not found: {workflow_path}")
            return error_response('Workflow file not found')
            
        # 加载工作流
        logger.info(f"Loading workflow from: {workflow_path}")
        workflow_data = load_workflow(workflow_path)
        
        # 构建变量映射
        variable_mapping = {}
        for var in variables:
            var_id = var.get('id')
            value = var.get('value')
            
            workflow_var = WorkflowVariable.query.filter_by(
                workflow_id=workflow_id,
                id=var_id
            ).first()
            
            if workflow_var:
                var_def = VariableDefinitions.query.get(workflow_var.class_type_id)
                if var_def:
                    # 构建新的变量映射格式：{node_id: {value_path: value}}
                    if workflow_var.node_id not in variable_mapping:
                        variable_mapping[workflow_var.node_id] = {}
                    variable_mapping[workflow_var.node_id][var_def.value_path] = value
        
        # 获取输出节点信息
        output_nodes = []
        for output_id in output_vars:
            workflow_var = WorkflowVariable.query.filter_by(
                workflow_id=workflow_id,
                id=output_id
            ).first()
            if workflow_var:
                output_nodes.append(workflow_var.node_id)
        
        logger.info(f"Variable mapping created: {variable_mapping}")
        logger.info(f"Output nodes: {output_nodes}")
        
        # 调用生成方法
        logger.info("Starting image generation process")
        try:
            result = prompt_to_image(
                workflow=workflow_data,
                variable_values=variable_mapping,
                output_node_ids=output_nodes,
                save_previews=True
            )
        except ValueError as e:
            logger.error("Invalid input parameters", exc_info=e)
            return error_response(str(e), 400)
        except RuntimeError as e:
            logger.error("Image generation failed", exc_info=e)
            return error_response(str(e), 500)
            
        logger.info(f"Image generation completed: {result}")
        
        # 保存图片信息到数据库
        try:
            image = Image(
                filename=os.path.basename(result[0]),
                workflow_id=workflow_id,
                workflow_name=workflow.name,
                file_path=os.path.join(OUTPUT_FOLDER, result[0]),
                variables=variable_mapping
            )
            db.session.add(image)
            db.session.commit()
            logger.info(f"Image record saved to database with ID: {image.id}")
        except Exception as e:
            logger.error("Failed to save image record to database", exc_info=e)
            # 即使数据库保存失败，仍然返回生成的图片
            return success_response({
                'message': 'Image generated but failed to save record',
                'result': result,
                'error': str(e)
            })

        return success_response({
            'message': 'Image generated successfully',
            'result': result,
            'image_info': image.to_dict()
        })

    except Exception as e:
        logger.exception("Unexpected error during image generation")
        return error_response(f'Image generation failed: {str(e)}', 500)

@bp.route('/list-images', methods=['GET'])
def list_images():
    try:
        logger.info("Starting image list request")
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        logger.info(f"Pagination parameters - page: {page}, page_size: {page_size}")
        
        if page < 1 or page_size < 1:
            logger.warning(f"Invalid pagination parameters: page={page}, page_size={page_size}")
            return error_response('Invalid pagination parameters')
        
        # Query images from database instead of filesystem
        pagination = Image.query.order_by(Image.created_at.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        logger.info(f"Found {pagination.total} total images, returning page {page} of {pagination.pages}")
        
        # Convert file paths to browsable URLs and remove prompt fields
        images = []
        for img in pagination.items:
            filename = os.path.basename(img.file_path)
            images.append({
                'id': img.id,
                'url': f'/images/output/{filename}',
                'created_at': img.created_at.isoformat(),
                'variables': img.variables
            })
        
        return success_response({
            'images': images,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_images': pagination.total,
                'total_pages': pagination.pages
            }
        })

    except ValueError:
        logger.warning("Invalid pagination parameters format")
        return error_response('Invalid pagination parameters')
    except Exception as e:
        logger.exception("Error while listing images")
        return error_response('Failed to list images', 500)

@bp.route('/image/<int:image_id>', methods=['GET'])
def get_image(image_id):
    try:
        logger.info(f"Retrieving details for image ID: {image_id}")
        
        image = Image.query.get_or_404(image_id)
        logger.info(f"Successfully retrieved image: {image.filename}")
        
        return success_response(image.to_dict())
    except Exception as e:
        logger.exception(f"Error while retrieving image {image_id}")
        return error_response('Failed to retrieve image details', 500) 