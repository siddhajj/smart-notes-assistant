import reflex as rx
from ..state.notes_state import NotesState

def note_modal() -> rx.Component:
    """Note modal for create/view/edit/delete operations"""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.hstack(
                        rx.heading(
                            rx.cond(
                                NotesState.note_modal_mode == "create",
                                "Create New Note",
                                rx.cond(
                                    NotesState.note_modal_mode == "view",
                                    "View Note", 
                                    "Edit Note"
                                )
                            ),
                            size="5"
                        ),
                        rx.spacer(),
                        rx.modal_close_button()
                    ),
                    width="100%"
                )
            ),
            rx.modal_body(
                rx.vstack(
                    # Title input
                    rx.form_control(
                        rx.form_label("Title", font_weight="semibold"),
                        rx.input(
                            placeholder="Enter note title...",
                            value=NotesState.note_title,
                            on_change=NotesState.set_note_title,
                            is_read_only=NotesState.note_modal_mode == "view",
                            size="lg"
                        ),
                        is_required=True,
                        margin_bottom="1rem"
                    ),
                    
                    # Body textarea
                    rx.form_control(
                        rx.form_label("Content", font_weight="semibold"),
                        rx.textarea(
                            placeholder="Write your note content here...",
                            value=NotesState.note_body,
                            on_change=NotesState.set_note_body,
                            is_read_only=NotesState.note_modal_mode == "view",
                            min_height="200px",
                            size="lg"
                        ),
                        margin_bottom="1rem"
                    ),
                    
                    # Tags input
                    rx.form_control(
                        rx.form_label("Tags", font_weight="semibold"),
                        rx.input(
                            placeholder="Enter tags separated by commas...",
                            value=NotesState.note_tags,
                            on_change=NotesState.set_note_tags,
                            is_read_only=NotesState.note_modal_mode == "view"
                        ),
                        margin_bottom="1.5rem"
                    ),
                    
                    # Error message
                    rx.cond(
                        NotesState.error_message,
                        rx.alert(
                            rx.alert_icon(),
                            rx.alert_title(NotesState.error_message),
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
                    # View mode buttons
                    rx.cond(
                        NotesState.note_modal_mode == "view",
                        rx.hstack(
                            rx.button(
                                "Edit",
                                on_click=NotesState.switch_to_edit_mode,
                                color_scheme="blue",
                                variant="outline"
                            ),
                            rx.button(
                                "Delete",
                                on_click=lambda: NotesState.delete_note(NotesState.current_note.id),
                                color_scheme="red",
                                variant="outline",
                                loading=NotesState.note_save_loading
                            ),
                            rx.button(
                                "Close",
                                on_click=NotesState.close_note_modal,
                                variant="ghost"
                            ),
                            spacing="2"
                        )
                    ),
                    
                    # Create/Edit mode buttons
                    rx.cond(
                        NotesState.note_modal_mode != "view",
                        rx.hstack(
                            rx.cond(
                                NotesState.note_modal_mode == "edit",
                                rx.button(
                                    "Delete",
                                    on_click=lambda: NotesState.delete_note(NotesState.current_note.id),
                                    color_scheme="red",
                                    variant="outline",
                                    loading=NotesState.note_save_loading
                                )
                            ),
                            rx.button(
                                "Cancel",
                                on_click=NotesState.close_note_modal,
                                variant="ghost"
                            ),
                            rx.button(
                                rx.cond(
                                    NotesState.note_modal_mode == "create",
                                    "Create Note",
                                    "Save Changes"
                                ),
                                on_click=NotesState.save_note,
                                color_scheme="blue",
                                loading=NotesState.note_save_loading
                            ),
                            spacing="2"
                        )
                    ),
                    
                    justify="end",
                    width="100%"
                ),
                padding="1rem 1.5rem"
            ),
            max_width="600px",
            margin="auto"
        ),
        is_open=NotesState.show_note_modal,
        on_close=NotesState.close_note_modal,
        close_on_overlay_click=False
    )