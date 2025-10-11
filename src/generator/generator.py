def generate_docs(tasks, feedback=None): # Add feedback parameter
    docs=[]
    
    # Check what the feedback is telling us to do
    use_detailed_descriptions = False
    if feedback and "Some methods still have placeholder descriptions." in feedback:
        use_detailed_descriptions = True
    
    for task in tasks:
        if task["task_type"]== "document_controller":
            # Pass the flag down
            docs.append(generate_controller_doc(task, use_detailed_descriptions))
        elif task["task_type"]== "document_service":
            docs.append(generate_service_doc(task))
        elif task["task_type"]== "document_entity":
            docs.append(generate_entity_doc(task))
    return "\n\n".join(docs)


def generate_controller_doc(task, use_detailed_descriptions=False): # Add flag
    class_name= task["class_name"]
    methods= task.get("methods",[])
    doc=f"## Controller: {class_name}\n"
    doc+="This controller manages Rest API endpoint. \n\n"
    doc+="**Endpoints:**\n"
    
    for m in methods:
        if use_detailed_descriptions:
            # The "improved" version based on feedback
            doc += f"- `{m}()` — This endpoint handles operations related to {m}. The request and response body should be documented.\n"
        else:
            # The initial, placeholder version
            doc += f"- `{m}()` — description TBD.\n"
    return doc
def generate_service_doc(task):
    class_name = task["class_name"]
    doc = f"## Service: {class_name}\n"
    doc += "Handles business logic and interactions with repositories.\n"
    return doc
def generate_entity_doc(task):
    class_name = task["class_name"]
    doc = f"## Entity: {class_name}\n"
    doc += "Represents a database table mapped with JPA annotations.\n"
    return doc
