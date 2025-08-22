import reflex as rx
from typing import List
from ..state.tasks_state import TasksState, Task

def task_item(task: Task) -> rx.Component:
    """Individual task item component"""
    return rx.box(
        rx.hstack(
            # Checkbox for completion
            rx.checkbox(
                is_checked=task.is_completed,
                on_change=lambda checked: TasksState.toggle_task_completion(task.id, checked),
                color_scheme="green",
                size="lg"
            ),
            
            # Task content
            rx.vstack(
                # Task description
                rx.text(
                    task.description,
                    font_size="0.95rem",
                    color=rx.cond(task.is_completed, "gray.500", "gray.800"),
                    text_decoration=rx.cond(task.is_completed, "line-through", "none"),
                    weight="medium",
                    line_height="1.4"
                ),
                
                # Task metadata
                rx.hstack(
                    # Priority badge
                    rx.badge(
                        task.priority.capitalize(),
                        color_scheme=TasksState.get_priority_color(task.priority),
                        size="sm"
                    ),
                    
                    # Due date
                    rx.cond(
                        task.due_date,
                        rx.text(
                            TasksState.format_due_date(task.due_date),
                            font_size="0.8rem",
                            color="gray.500"
                        )
                    ),
                    
                    # Tags
                    rx.cond(
                        task.tags,
                        rx.wrap(
                            rx.foreach(
                                task.tags,
                                lambda tag: rx.badge(
                                    tag,
                                    color_scheme="gray",
                                    size="sm",
                                    variant="outline"
                                )
                            ),
                            spacing="0.25rem"
                        )
                    ),
                    
                    spacing="2",
                    flex_wrap="wrap"
                ),
                
                align="start",
                spacing="1",
                flex="1"
            ),
            
            # Delete button
            rx.icon_button(
                rx.icon("x", size=16),
                on_click=lambda: TasksState.delete_task(task.id),
                variant="ghost",
                color_scheme="red",
                size="sm",
                _hover={"background": "red.100"}
            ),
            
            width="100%",
            align="start",
            spacing="3"
        ),
        
        padding="1rem",
        border="1px solid",
        border_color="gray.200",
        border_radius="md",
        background="white",
        margin_bottom="0.5rem",
        width="100%",
        _hover={"border_color": "gray.300"},
        transition="border-color 0.2s ease"
    )

def tasks_list() -> rx.Component:
    """Tasks list component"""
    return rx.cond(
        TasksState.tasks_loading,
        # Loading state
        rx.vstack(
            rx.spinner(size="lg"),
            rx.text("Loading tasks...", color="gray.500"),
            align="center",
            spacing="2",
            padding="2rem"
        ),
        # Tasks content
        rx.cond(
            TasksState.get_visible_tasks(),
            # Has tasks
            rx.vstack(
                rx.foreach(TasksState.get_visible_tasks(), task_item),
                width="100%",
                spacing="0",
                align="start"
            ),
            # No tasks
            rx.center(
                rx.vstack(
                    rx.icon("check-square", size=48, color="gray.400"),
                    rx.text(
                        "No tasks yet",
                        font_size="lg",
                        color="gray.500",
                        weight="semibold"
                    ),
                    rx.text(
                        "Create your first task to get started",
                        font_size="sm",
                        color="gray.400"
                    ),
                    spacing="2",
                    align="center"
                ),
                padding="3rem"
            )
        )
    )

def tasks_section() -> rx.Component:
    """Main tasks section component"""
    return rx.box(
        rx.vstack(
            # Section header
            rx.hstack(
                rx.heading(
                    "Tasks",
                    size="6",
                    color="gray.800",
                    weight="bold"
                ),
                rx.spacer(),
                
                # Action buttons
                rx.hstack(
                    # Show completed toggle
                    rx.switch(
                        is_checked=TasksState.show_completed_tasks,
                        on_change=TasksState.toggle_completed_tasks,
                        color_scheme="blue",
                        size="sm"
                    ),
                    rx.text(
                        "Show completed",
                        font_size="0.9rem",
                        color="gray.600"
                    ),
                    
                    rx.cond(
                        TasksState.tasks_expanded,
                        rx.button(
                            rx.icon("minimize-2", size=16),
                            "Collapse",
                            on_click=TasksState.reset_panels,
                            variant="ghost",
                            size="sm",
                            color_scheme="gray"
                        ),
                        rx.button(
                            rx.icon("maximize-2", size=16),
                            "Expand",
                            on_click=TasksState.expand_tasks,
                            variant="ghost",
                            size="sm",
                            color_scheme="gray"
                        )
                    ),
                    
                    rx.button(
                        rx.icon("plus", size=16),
                        "New Task",
                        on_click=TasksState.show_create_task_modal,
                        color_scheme="green",
                        size="sm"
                    ),
                    
                    spacing="3"
                ),
                width="100%",
                align="center",
                margin_bottom="1rem"
            ),
            
            # Tasks list
            rx.box(
                tasks_list(),
                width="100%",
                height="100%",
                overflow_y="auto",
                max_height="calc(80vh - 120px)"  # Account for header and chat
            ),
            
            align="start",
            spacing="0",
            width="100%",
            height="100%"
        ),
        
        # Conditional width based on expansion state
        width=rx.cond(
            TasksState.tasks_expanded,
            "100%",
            rx.cond(
                TasksState.notes_expanded,
                "0%",  # Hidden when notes expanded
                "50%"  # Default 50/50 split
            )
        ),
        
        # Conditional visibility
        display=rx.cond(
            TasksState.notes_expanded,
            "none",
            "block"
        ),
        
        padding="1.5rem",
        height="100%",
        background="white",
        transition="all 0.3s ease"
    )