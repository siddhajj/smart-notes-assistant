import reflex as rx
from ..state.tasks_state import TasksState

def task_modal() -> rx.Component:
    """Task modal for creating new tasks"""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.hstack(
                        rx.heading("Create New Task", size="5"),
                        rx.spacer(),
                        rx.modal_close_button()
                    ),
                    width="100%"
                ),
                rx.modal_body(
                    rx.vstack(
                        # Description input
                        rx.form_control(
                            rx.form_label("Description", font_weight="semibold"),
                            rx.textarea(
                                placeholder="What needs to be done?",
                                value=TasksState.task_description,
                                on_change=TasksState.set_task_description,
                                min_height="100px",
                                size="lg"
                            ),
                            is_required=True,
                            margin_bottom="1rem"
                        ),
                        
                        # Due date input
                        rx.form_control(
                            rx.form_label("Due Date (Optional)", font_weight="semibold"),
                            rx.input(
                                type="date",
                                value=TasksState.task_due_date,
                                on_change=TasksState.set_task_due_date,
                                size="lg"
                            ),
                            margin_bottom="1rem"
                        ),
                        
                        # Priority select
                        rx.form_control(
                            rx.form_label("Priority", font_weight="semibold"),
                            rx.select(
                                ["low", "medium", "high", "urgent"],
                                value=TasksState.task_priority,
                                on_change=TasksState.set_task_priority,
                                size="lg"
                            ),
                            margin_bottom="1rem"
                        ),
                        
                        # Tags input
                        rx.form_control(
                            rx.form_label("Tags (Optional)", font_weight="semibold"),
                            rx.input(
                                placeholder="Enter tags separated by commas...",
                                value=TasksState.task_tags,
                                on_change=TasksState.set_task_tags,
                                size="lg"
                            ),
                            margin_bottom="1.5rem"
                        ),
                        
                        # Error message
                        rx.cond(
                            TasksState.error_message,
                            rx.alert(
                                rx.alert_icon(),
                                rx.alert_title(TasksState.error_message),
                                status="error",
                                margin_bottom="1rem"
                            )
                        ),
                        
                        spacing="0",
                        width="100%"
                    ),
                    padding="1.5rem"
                ),
                rx.modal_footer(
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            on_click=TasksState.close_task_modal,
                            variant="ghost"
                        ),
                        rx.button(
                            "Create Task",
                            on_click=TasksState.save_task,
                            color_scheme="green",
                            loading=TasksState.task_save_loading
                        ),
                        spacing="2",
                        justify="end",
                        width="100%"
                    ),
                    padding="1rem 1.5rem"
                ),
                max_width="500px",
                margin="auto"
            )
        ),
        is_open=TasksState.show_task_modal,
        on_close=TasksState.close_task_modal,
        close_on_overlay_click=False
    )