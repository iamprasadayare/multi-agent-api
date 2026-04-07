import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
from database import add_task, get_tasks, add_note

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

task_tools = Tool(function_declarations=[add_task_func, get_tasks_func, add_note_func])

model = GenerativeModel(
    "gemini-2.5-flash",
    tools=[task_tools],
    system_instruction="You are an AI assistant managing the user's tasks and notes. Use the provided tools appropriately."
)
chat_session = model.start_chat()

async def process_request(user_input: str) -> str:
    response = chat_session.send_message(user_input)
    
    # Handle multiple parallel tool calls sequentially with a loop!
    while response.candidates and response.candidates[0].function_calls:
        function_responses = []
        for fc in response.candidates[0].function_calls:
            if fc.name == "add_task": 
                result = add_task(fc.args.get("description", ""))
            elif fc.name == "get_tasks": 
                result = get_tasks()
            elif fc.name == "add_note": 
                result = add_note(fc.args.get("content", ""))
            else: 
                result = "Unknown function"
            
            function_responses.append(
                Part.from_function_response(name=fc.name, response={"result": str(result)})
            )
            
        # Send all execution results simultaneously back to the AI
        response = chat_session.send_message(function_responses)
        
    return response.text
