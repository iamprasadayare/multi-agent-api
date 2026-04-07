from google.cloud import firestore
# Automatically uses the Google Cloud environment's default credentials
db = firestore.Client()
def add_task(description: str) -> str:
    """Adds a task to Firestore."""
    doc_ref = db.collection("tasks").document()
    doc_ref.set({"description": description, "status": "pending"})
    return f"Task added with ID: {doc_ref.id}"
def get_tasks() -> str:
    """Gets all tasks from Firestore."""
    tasks = db.collection("tasks").stream()
    return str([{"id": t.id, **t.to_dict()} for t in tasks])
def add_note(note: str) -> str:
    """Adds a note to Firestore."""
    doc_ref = db.collection("notes").document()
    doc_ref.set({"content": note})
    return f"Note added with ID: {doc_ref.id}"
