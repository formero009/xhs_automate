from comfyui_api.api.api_helpers import generate_image_by_prompt
from comfyui_api.utils.helpers.randomize_seed import generate_random_15_digit_number
from comfyui_api.api.open_websocket import open_websocket_connection
from conf import OUTPUT_FOLDER
import os
from typing import List, Dict, Union
import json
import copy
import logging
from app.utils.logger import logger

def prompt_to_image(
    workflow: Union[dict, str],
    variable_values: Dict[str, Dict[str, any]],
    output_node_ids: list,
    save_previews: bool = True
) -> list:
    """
    根据提供的变量值生成图片
    
    Args:
        workflow: 工作流配置字典或JSON字符串
        variable_values: 变量值映射字典，格式为 {node_id: {value_path: value}}
        output_node_ids: 输出节点ID列表
        save_previews: 是否保存预览图
    
    Returns:
        list: 生成的图片文件路径列表
        
    Raises:
        ValueError: 当输入参数无效时
        RuntimeError: 当图片生成过程失败时
    """
    try:
        # 如果 workflow 是字符串，则解析为字典
        if isinstance(workflow, str):
            workflow = json.loads(workflow)
        
        # 深拷贝工作流以避免修改原始数据
        workflow = copy.deepcopy(workflow)
        
        # 遍历所有需要修改的节点
        for node_id, node_variables in variable_values.items():
            if node_id in workflow:
                node = workflow[node_id]
                inputs = node.get('inputs', {})
                
                # 遍历该节点的所有变量映射
                for value_path, value in node_variables.items():
                    # value_path 格式为 "inputs.text" 或类似格式
                    path_parts = value_path.split('.')
                    
                    # 如果路径以 "inputs" 开头
                    if path_parts[0] == 'inputs' and len(path_parts) > 1:
                        input_key = path_parts[1]
                        if input_key in inputs:
                            inputs[input_key] = value
            else:
                logger.warning(f"Node ID {node_id} not found in workflow")
        
        # 调用 ComfyUI API 生成图片
        prompt = workflow
        
        # 设置随机种子
        # try:
        #     id_to_class_type = {id: details['class_type'] for id, details in prompt.items()}
        #     random_seed = [key for key, value in id_to_class_type.items() if 'seed _O' in value][0]
        #     prompt.get(random_seed)['inputs']['seed'] = generate_random_15_digit_number()
        # except (KeyError, IndexError) as e:
        #     logger.warning("Failed to set random seed, continuing with default seed", exc_info=e)

        # 使用指定的输出节点
        output_files = []
        generation_errors = []
        
        for output_id in output_node_ids:
            if output_id not in prompt:
                logger.error(f"Output node ID {output_id} not found in workflow")
                generation_errors.append(f"Output node {output_id} not found")
                continue
                
            try:
                result = generate_image_by_prompt(prompt, OUTPUT_FOLDER, output_id, save_previews)
                if not result:
                    logger.error(f"Failed to generate image for output node {output_id}")
                    generation_errors.append(f"Failed to generate image for output node {output_id}")
                    continue
                output_files.extend(result)
            except Exception as e:
                error_msg = f"Failed to generate image for output node {output_id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                generation_errors.append(error_msg)
        
        if not output_files and generation_errors:
            # 如果没有成功生成任何图片，抛出异常
            raise RuntimeError(f"Image generation failed: {'; '.join(generation_errors)}")
        
        logger.info(f"Successfully generated {len(output_files)} images")
        return output_files

    except json.JSONDecodeError as e:
        error_msg = "Invalid workflow JSON format"
        logger.error(error_msg, exc_info=e)
        raise ValueError(error_msg) from e
        
    except Exception as e:
        error_msg = f"Error during image generation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e