import pynecone as pc
from datetime import date

class TasksListState(pc.State):
    tasks: list = []
    error_message: str = ""
    show_delete_dialog: bool = False
    task_to_delete_id: str = ""

    async def get_tasks(self):
        try:
            response = await pc.api.get("/tasks")
            if response.status_code == 200:
                self.tasks = response.json()
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to fetch tasks.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

    async def toggle_task_completed(self, task_id: str, current_status: bool):
        try:
            response = await pc.api.put(
                f"/tasks/{task_id}",
                {
                    "description": "", # Description is required by schema, but not changed here
                    "is_completed": not current_status
                }
            )
            if response.status_code == 200:
                await self.get_tasks() # Refresh the list
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to update task status.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

    def open_delete_dialog(self, task_id: str):
        self.task_to_delete_id = task_id
        self.show_delete_dialog = True

    def close_delete_dialog(self):
        self.show_delete_dialog = False
        self.task_to_delete_id = ""

    async def handle_delete_task(self):
        try:
            response = await pc.api.delete(f"/tasks/{self.task_to_delete_id}")
            if response.status_code == 204:
                await self.get_tasks() # Refresh the list
                self.close_delete_dialog()
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to delete task.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def tasks_list():
    return pc.center(
        pc.vstack(
            pc.heading("My Tasks"),
            pc.cond(
                TasksListState.error_message != "",
                pc.text(TasksListState.error_message, color="red")
            ),
            pc.cond(
                len(TasksListState.tasks) == 0,
                pc.text("No tasks found. Create one!"),
                pc.foreach(
                    TasksListState.tasks,
                    lambda task: pc.box(
                        pc.hstack(
                            pc.checkbox(
                                is_checked=task["is_completed"],
                                on_change=lambda: TasksListState.toggle_task_completed(task["id"], task["is_completed"])
                            ),
                            pc.text(task["description"], text_decoration=pc.cond(task["is_completed"], "line-through", "none")),
                            pc.text(f"Due: {task["due_date"]}" if task["due_date"] else "", font_size="sm", color="gray.500"),
                            pc.link("Edit", href=f"/tasks/{task["id"]}/edit"),
                            pc.button("Delete", on_click=lambda: TasksListState.open_delete_dialog(task["id"])),
                        ),
                        border_width="1px",
                        padding="10px",
                        margin_y="5px",
                        width="100%"
                    )
                )
            ),
            pc.link("Create New Task", href="/create_task"),
            pc.cond(
                TasksListState.show_delete_dialog,
                pc.alert_dialog(
                    pc.alert_dialog_overlay(
                        pc.alert_dialog_content(
                            pc.alert_dialog_header("Confirm Deletion"),
                            pc.alert_dialog_body("Are you sure you want to delete this task? This action cannot be undone."),
                            pc.alert_dialog_footer(
                                pc.button("Cancel", on_click=TasksListState.close_delete_dialog),
                                pc.button("Delete", on_click=TasksListState.handle_delete_task, color_scheme="red"),
                            ),
                        )
                    )
                ),
            ),
        ),
        width="100vw",
        height="100vh",
        on_load=TasksListState.get_tasks
    )