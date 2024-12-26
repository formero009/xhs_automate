import json
from typing import Tuple, Any, Optional

def get_json_value_with_type(json_data: dict, path: str) -> Tuple[Optional[Any], Optional[str]]:
    """
    根据路径获取 JSON 内容中的值及其类型，并进行类型标准化。
    
    Args:
        json_data: JSON 数据字典
        path: 字符串路径，例如 "inputs.text" 或 "inputs.clip"
    
    Returns:
        Tuple[Any, str]: 返回 (值, 标准化类型名称) 或 (None, None)
        标准化类型包括: 'string', 'long', 'float', 'boolean', 'array', 'object'
    """
    def normalize_type(value: Any) -> str:
        """标准化类型名称"""
        if isinstance(value, str):
            return 'string'
        elif isinstance(value, int):
            return 'long'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        elif value is None:
            return 'null'
        return type(value).__name__

    try:
        # 如果是JSON字符串，先解析
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        # 按路径分割并遍历
        current = json_data
        for key in path.split('.'):
            current = current[key]
        
        # 获取标准化类型
        value_type = normalize_type(current)
        return current, value_type
        
    except (KeyError, TypeError, json.JSONDecodeError):
        return None, None