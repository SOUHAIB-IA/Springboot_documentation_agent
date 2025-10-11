import os 


def load_java_files(project_path):
    java_files=[]
    for root,dirs,files in os.walk(project_path):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root,file))
    return java_files


        