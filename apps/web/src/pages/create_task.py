import pynecone as pc
from datetime import date

class CreateTaskState(pc.State):
    description: str
    due_date: str
    error_message: str = ""

    async def handle_create_task(self):
        try:
            # Convert due_date string to date object if provided
            due_date_obj = None
            if self.due_date:
                try:
                    due_date_obj = date.fromisoformat(self.due_date)
                except ValueError:
                    self.error_message = "Invalid date format. Use YYYY-MM-DD."
                    return

            response = await pc.api.post(
                "/tasks",
                {
                    "description": self.description,
                    "due_date": due_date_obj.isoformat() if due_date_obj else None
                }
            )
            if response.status_code == 201:
                return pc.redirect("/tasks") # Redirect to tasks list on success
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to create task.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def create_task():
    return pc.center(
        pc.vstack(
            pc.heading("Create New Task"),
            pc.input(placeholder="Description", on_change=CreateTaskState.set_description),
            pc.input(placeholder="Due Date (YYYY-MM-DD)", on_change=CreateTaskState.set_due_date),
            pc.button("Create Task", on_click=CreateTaskState.handle_create_task),
            pc.cond(CreateTaskState.error_message != "", pc.text(CreateTaskState.error_message, color="red")),
            pc.link("Back to Tasks", href="/tasks"),
        ),
        width="100vw",
        height="100vh",
    )
