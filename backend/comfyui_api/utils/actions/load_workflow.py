import json

def load_workflow(workflow_path):
    try:
        print('path:', workflow_path)
        # 显式指定编码为 utf-8
        with open(workflow_path, 'r', encoding='utf-8') as file:
            workflow = json.load(file)
            return json.dumps(workflow)
    except FileNotFoundError:
        print(f"The file {workflow_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"The file {workflow_path} contains invalid JSON.")
        return None