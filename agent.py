import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
from database import add_task, get_tasks, add_note, mark_task_complete, delete_task

vertexai.init()

add_task_func = FunctionDeclaration(
    name="add_task",
    description="Adds a new task to the user's checklist. Provide the 'description'.",
    parameters={"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]}
)

get_tasks_func = FunctionDeclaration(
    name="get_tasks",
    description="Gets all the user's current tasks.",
    parameters={"type": "object", "properties": {}}
)

add_note_func = FunctionDeclaration(
    name="add_note",
    description="Saves a note or piece of information. Provide the 'content'.",
    parameters={"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}
)

mark_task_complete_func = FunctionDeclaration(
    name="mark_task_complete",
    description="Marks a specific task as completed. Provide the 'task_id'.",
    parameters={"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}
)

delete_task_func = FunctionDeclaration(
    name="delete_task",
    description="Deletes a specific task. Provide the 'task_id'.",
    parameters={"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}
)

task_tools = Tool(function_declarations=[add_task_func, get_tasks_func, add_note_func, mark_task_complete_func, delete_task_func])

model = GenerativeModel(
    "gemini-2.5-flash",
    tools=[task_tools],
    system_instruction="You are a helpful AI assistant managing tasks. CRITICAL: NEVER display the raw task IDs to the user. Keep them completely hidden internally. If asked to delete multiple tasks, first retrieve the tasks, then call delete_task individually for EACH task ID that matches the user's request."
)
chat_session = model.start_chat()

async def process_request(user_input: str) -> str:
    response = chat_session.send_message(user_input)
    
    # Handle multiple parallel tool calls sequentially with a loop!
    while response.candidates and response.candidates[0].function_calls:
        function_responses = []
        for fc in response.candidates[0].function_calls:
            try:
                if fc.name == "add_task": 
                    result = add_task(fc.args.get("description", ""))
                elif fc.name == "get_tasks": 
                    result = get_tasks()
                elif fc.name == "add_note": 
                    result = add_note(fc.args.get("content", ""))
                elif fc.name == "mark_task_complete":
                    # ensure task_id isn't somehow empty
                    task_id = fc.args.get("task_id", "")
                    if not task_id: 
                        raise ValueError("Missing task_id.")
                    result = mark_task_complete(task_id)
                elif fc.name == "delete_task":
                    task_id = fc.args.get("task_id", "")
                    if not task_id: 
                        raise ValueError("Missing task_id.")
                    result = delete_task(task_id)
                else: 
                    result = "Unknown function"
            except Exception as e:
                # If python throws an error (e.g invalid task ID), pass it back to the AI calmly!
                result = f"Error executing tool: {str(e)}"
            
            function_responses.append(
                Part.from_function_response(name=fc.name, response={"result": str(result)})
            )
            
        # Send all execution results simultaneously back to the AI
        response = chat_session.send_message(function_responses)
        
    return response.text
