import javalang

def parse_java_file(file_path):
    with open(file_path, 'r') as file:
        java_code = file.read()
    
    try:
        tree = javalang.parse.parse(java_code)
        classes_info = []
        for _, class_node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = class_node.name
            class_annotations = [ann.name for ann in class_node.annotations]
            
            methods_info = []
            for method in class_node.methods:
                params = []
                if method.parameters:
                    for param in method.parameters:
                        # Handle varargs if necessary
                        param_type = param.type.name
                        if isinstance(param.type, javalang.tree.ReferenceType) and param.type.arguments:
                            generic_type = param.type.arguments[0].type.name
                            param_type = f"{param_type}<{generic_type}>"
                        params.append({"name": param.name, "type": param_type})

                method_info = {
                    "method_name": method.name,
                    "annotations": [ann.name for ann in method.annotations],
                    "parameters": params,
                    "return_type": method.return_type.name if method.return_type else "void"
                }
                methods_info.append(method_info)

            fields_info = []
            for field in class_node.fields:
                field_type = field.type.name
                # Assuming one declarator per field for simplicity
                field_name = field.declarators[0].name
                fields_info.append({"name": field_name, "type": field_type})

            class_info = {
                "class_name": class_name,
                "annotations": class_annotations,
                "methods": methods_info,
                "fields": fields_info
            }
            classes_info.append(class_info)
                
        return classes_info
    except (javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError) as e:
        print(f"Syntax error in file {file_path}: {e}")
        return None