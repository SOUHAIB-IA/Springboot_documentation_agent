
def plan_documentation(project_info):
    tasks=[]
    
    for controller in project_info.get("controllers",[]):
        task={
            "task_type":"document_controller",
            "class_name":controller["class_name"], # Corrected
            "methods":[method["method_name"] for method in controller["methods"]] 
        }
        tasks.append(task)
        
    for service in project_info.get("services",[]):
        task={
            "task_type":"document_service",
            "class_name":service["class_name"]
        }
        tasks.append(task)
        
    for entity in project_info.get("entities",[]):
        task={
            "task_type":"document_entity",
            "class_name": entity["class_name"]
        }
        tasks.append(task)
    return tasks