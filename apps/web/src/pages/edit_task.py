import pynecone as pc
from datetime import date

class EditTaskState(pc.State):
    task_id: str
    description: str
    due_date: str
    error_message: str = ""
    show_delete_dialog: bool = False

    @pc.var
    def get_task_id(self) -> str:
        return self.router.page.params.get("task_id", "")

    async def get_task_details(self):
        if not self.get_task_id:
            return
        try:
            response = await pc.api.get(f"/tasks/{self.get_task_id}")
            if response.status_code == 200:
                task_data = response.json()
                self.description = task_data["description"]
                self.due_date = task_data["due_date"]
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to fetch task details.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

    async def handle_update_task(self):
        try:
            # Convert due_date string to date object if provided
            due_date_obj = None
            if self.due_date:
                try:
                    due_date_obj = date.fromisoformat(self.due_date)
                except ValueError:
                    self.error_message = "Invalid date format. Use YYYY-MM-DD."
                    return

            response = await pc.api.put(
                f"/tasks/{self.get_task_id}",
                {
                    "description": self.description,
                    "due_date": due_date_obj.isoformat() if due_date_obj else None
                }
            )
            if response.status_code == 200:
                return pc.redirect(f"/tasks/{self.get_task_id}") # Redirect to view task on success
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to update task.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

    def toggle_delete_dialog(self):
        self.show_delete_dialog = not self.show_delete_dialog

    async def handle_delete_task(self):
        try:
            response = await pc.api.delete(f"/tasks/{self.get_task_id}")
            if response.status_code == 204:
                return pc.redirect("/tasks") # Redirect to tasks list on success
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to delete task.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def edit_task():
    return pc.center(
        pc.vstack(
            pc.heading("Edit Task"),
            pc.input(placeholder="Description", value=EditTaskState.description, on_change=EditTaskState.set_description),
            pc.input(placeholder="Due Date (YYYY-MM-DD)", value=EditTaskState.due_date, on_change=EditTaskState.set_due_date),
            pc.button("Update Task", on_click=EditTaskState.handle_update_task),
            pc.cond(EditTaskState.error_message != "", pc.text(EditTaskState.error_message, color="red")),
            pc.hstack(
                pc.link("Cancel", href=f"/tasks/{EditTaskState.get_task_id}"),
                pc.button("Delete Task", on_click=EditTaskState.toggle_delete_dialog),
            ),
            pc.cond(
                EditTaskState.show_delete_dialog,
                pc.alert_dialog(
                    pc.alert_dialog_overlay(
                        pc.alert_dialog_content(
                            pc.alert_dialog_header("Confirm Deletion"),
                            pc.alert_dialog_body("Are you sure you want to delete this task? This action cannot be undone."),
                            pc.alert_dialog_footer(
                                pc.button("Cancel", on_click=EditTaskState.toggle_delete_dialog),
                                pc.button("Delete", on_click=EditTaskState.handle_delete_task, color_scheme="red"),
                            ),
                        )
                    )
                ),
            ),
        ),
        width="100vw",
        height="100vh",
        on_load=EditTaskState.get_task_details
    )
