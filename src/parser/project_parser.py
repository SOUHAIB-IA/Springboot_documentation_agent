from parser.file_loader import load_java_files
from parser.java_parser import parse_java_file


def parse_project(project_path):
    java_files= load_java_files(project_path)
    project_info={"controllers":[],"services":[],"entities":[]}
    for java_file in java_files:
        class_info= parse_java_file(java_file)
        if class_info: 
            for class_data in class_info:
                annotations = class_data.get("annotations", [])
                
                if any("Controller" in ann for ann in annotations):
                    project_info["controllers"].append(class_data)
                elif any("Service" in ann for ann in annotations):
                    project_info["services"].append(class_data)
                elif any("Entity" in ann for ann in annotations):
                    project_info["entities"].append(class_data)
    return project_info
