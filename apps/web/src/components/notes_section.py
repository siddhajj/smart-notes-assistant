import reflex as rx
from typing import List
from ..state.notes_state import NotesState, Note

def note_item(note: Note) -> rx.Component:
    """Individual note item component"""
    return rx.box(
        rx.vstack(
            # Note header with title
            rx.hstack(
                rx.heading(
                    note.title,
                    size="4",
                    color="gray.800",
                    weight="semibold",
                    margin_bottom="0.5rem"
                ),
                rx.spacer(),
                rx.text(
                    note.updated_at[:10] if len(note.updated_at) > 10 else note.updated_at,
                    font_size="0.8rem",
                    color="gray.500"
                ),
                width="100%",
                align="start"
            ),
            
            # Note preview
            rx.text(
                NotesState.get_note_preview(note, 120),
                font_size="0.9rem",
                color="gray.600",
                line_height="1.4",
                margin_bottom="0.5rem"
            ),
            
            # Tags
            rx.cond(
                note.tags,
                rx.wrap(
                    rx.foreach(
                        note.tags,
                        lambda tag: rx.badge(
                            tag,
                            color_scheme="blue",
                            size="sm"
                        )
                    ),
                    spacing="0.25rem"
                )
            ),
            
            align="start",
            spacing="1",
            width="100%"
        ),
        
        # Click handler to view note
        on_click=lambda: NotesState.show_view_note_modal(note),
        cursor="pointer",
        padding="1rem",
        border="1px solid",
        border_color="gray.200",
        border_radius="md",
        background="white",
        _hover={
            "border_color": "blue.300",
            "shadow": "md"
        },
        transition="all 0.2s ease",
        margin_bottom="0.75rem",
        width="100%"
    )

def notes_list() -> rx.Component:
    """Notes list component"""
    return rx.cond(
        NotesState.notes_loading,
        # Loading state
        rx.vstack(
            rx.spinner(size="lg"),
            rx.text("Loading notes...", color="gray.500"),
            align="center",
            spacing="2",
            padding="2rem"
        ),
        # Notes content
        rx.cond(
            NotesState.notes,
            # Has notes
            rx.vstack(
                rx.foreach(NotesState.notes, note_item),
                width="100%",
                spacing="0",
                align="start"
            ),
            # No notes
            rx.center(
                rx.vstack(
                    rx.icon("file-text", size=48, color="gray.400"),
                    rx.text(
                        "No notes yet",
                        font_size="lg",
                        color="gray.500",
                        weight="semibold"
                    ),
                    rx.text(
                        "Create your first note to get started",
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

def notes_section() -> rx.Component:
    """Main notes section component"""
    return rx.box(
        rx.vstack(
            # Section header
            rx.hstack(
                rx.heading(
                    "Notes",
                    size="6",
                    color="gray.800",
                    weight="bold"
                ),
                rx.spacer(),
                
                # Action buttons
                rx.hstack(
                    rx.cond(
                        NotesState.notes_expanded,
                        rx.button(
                            rx.icon("minimize-2", size=16),
                            "Collapse",
                            on_click=NotesState.reset_panels,
                            variant="ghost",
                            size="sm",
                            color_scheme="gray"
                        ),
                        rx.button(
                            rx.icon("maximize-2", size=16),
                            "Expand",
                            on_click=NotesState.expand_notes,
                            variant="ghost",
                            size="sm",
                            color_scheme="gray"
                        )
                    ),
                    
                    rx.button(
                        rx.icon("plus", size=16),
                        "New Note",
                        on_click=NotesState.show_create_note_modal,
                        color_scheme="blue",
                        size="sm"
                    ),
                    
                    spacing="2"
                ),
                width="100%",
                align="center",
                margin_bottom="1rem"
            ),
            
            # Notes list
            rx.box(
                notes_list(),
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
            NotesState.notes_expanded,
            "100%",
            rx.cond(
                NotesState.tasks_expanded,
                "0%",  # Hidden when tasks expanded
                "50%"  # Default 50/50 split
            )
        ),
        
        # Conditional visibility
        display=rx.cond(
            NotesState.tasks_expanded,
            "none",
            "block"
        ),
        
        padding="1.5rem",
        border_right=rx.cond(
            NotesState.notes_expanded | NotesState.tasks_expanded,
            "none",
            "1px solid var(--chakra-colors-gray-200)"
        ),
        height="100%",
        background="gray.50",
        transition="all 0.3s ease"
    )