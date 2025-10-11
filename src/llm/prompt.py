def get_controller_prompt(class_name, methods_data):
    method_signatures = []
    for m in methods_data:
        params = ", ".join([f"{p['type']} {p['name']}" for p in m['parameters']])
        signature = f"- {m['return_type']} {m['method_name']}({params}) with annotations {m['annotations']}"
        method_signatures.append(signature)
    
    signatures_str = "\n".join(method_signatures)

    return f"""
You are an expert technical writer assigned to document a Spring Boot REST controller.
Your task is to generate comprehensive and clear documentation in Markdown format.

**Controller Name:** `{class_name}`

**Methods to document:**
{signatures_str}

**Instructions:**
1.  Create a top-level heading for the controller.
2.  Write a brief, one-paragraph overview of the controller's purpose.
3.  For each method, create a subheading.
4.  Describe the endpoint's purpose, HTTP method (infer from annotations like @GetMapping, @PostMapping), and URL path.
5.  List and describe each parameter.
6.  Describe the expected success response, including status code and a sample JSON body if applicable.
7.  Describe potential error responses (e.g., 404 Not Found, 400 Bad Request).

Generate the documentation now.
"""

def get_entity_prompt(class_name, fields_data):
    fields_str = "\n".join([f"- {f['type']} {f['name']}" for f in fields_data])
    return f"""
You are an expert technical writer documenting a JPA Entity for a Spring Boot application.
Your task is to generate clear documentation in Markdown format.

**Entity Name:** `{class_name}`

**Fields:**
{fields_str}

**Instructions:**
1.  Create a top-level heading for the entity.
2.  Write a brief overview explaining what this entity represents in the application's domain.
3.  Create a "Fields" section.
4.  List each field in a table with columns: "Field Name", "Data Type", and "Description".
5.  Provide a concise description for each field.

Generate the documentation now.
"""
