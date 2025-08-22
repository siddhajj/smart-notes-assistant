import reflex as rx
from src.state.main_state import MainState
from src.state.notes_state import NotesState
from src.state.tasks_state import TasksState
from src.state.search_state import SearchState
from src.components.auth_modal import AuthState, auth_modal
from src.components.header import header
from src.components.notes_section import notes_section
from src.components.tasks_section import tasks_section
from src.components.note_modal import note_modal
from src.components.task_modal import task_modal
from src.components.search_interface import search_input, search_results_view

# Main application state that combines all states
class AppState(MainState, NotesState, TasksState, SearchState, AuthState):
    """Combined application state"""
    
    async def on_load(self):
        """Load initial data when app starts"""
        if self.is_authenticated:
            await self.load_notes()
            await self.load_tasks()

def default_view() -> rx.Component:
    """Default notes and tasks view"""
    return rx.hstack(
        notes_section(),
        tasks_section(),
        width="100%",
        height="80vh",
        spacing="0",
        align="start"
    )

def main_content() -> rx.Component:
    """Main content area that switches between default and search views"""
    return rx.cond(
        AppState.current_mode == "search",
        search_results_view(),
        default_view()
    )

def unauthenticated_view() -> rx.Component:
    """View shown to unauthenticated users"""
    return rx.center(
        rx.vstack(
            rx.icon("lock", size=64, color="gray.400"),
            rx.heading(
                "Welcome to Notes & Tasks",
                size="8",
                color="gray.600",
                text_align="center"
            ),
            rx.text(
                "Please log in or create an account to access your notes and tasks",
                font_size="lg",
                color="gray.500",
                text_align="center",
                max_width="500px"
            ),
            rx.hstack(
                rx.button(
                    "Login",
                    on_click=AppState.show_login_modal,
                    color_scheme="blue",
                    size="lg"
                ),
                rx.button(
                    "Sign Up",
                    on_click=AppState.show_register_modal,
                    variant="outline",
                    color_scheme="blue",
                    size="lg"
                ),
                spacing="4"
            ),
            spacing="6",
            align="center",
            text_align="center"
        ),
        width="100vw",
        height="80vh"
    )

def chat_area() -> rx.Component:
    """Chat/search area at the bottom"""
    return rx.box(
        search_input(),
        width="100%",
        height="20vh",
        background="gray.50",
        border_top="1px solid var(--chakra-colors-gray-200)",
        display=rx.cond(AppState.is_authenticated, "block", "none")
    )

def error_display() -> rx.Component:
    """Error message display"""
    return rx.cond(
        AppState.error_message,
        rx.alert(
            rx.alert_icon(),
            rx.alert_title(AppState.error_message),
            rx.alert_description("Please try again or refresh the page."),
            rx.close_button(
                on_click=AppState.clear_error,
                position="absolute",
                right="8px",
                top="8px"
            ),
            status="error",
            position="fixed",
            top="80px",
            right="20px",
            max_width="400px",
            z_index="1000"
        )
    )

def index() -> rx.Component:
    """Main application page"""
    return rx.box(
        # Header
        header(),
        
        # Main content
        rx.cond(
            AppState.is_authenticated,
            rx.vstack(
                main_content(),
                chat_area(),
                spacing="0",
                width="100%"
            ),
            unauthenticated_view()
        ),
        
        # Modals
        auth_modal(),
        note_modal(),
        task_modal(),
        
        # Error display
        error_display(),
        
        width="100vw",
        height="100vh",
        background="gray.50",
        overflow="hidden"
    )

# Configure the app
app = rx.App(
    state=AppState,
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        radius="medium"
    )
)

# Add pages
app.add_page(
    index,
    title="Notes & Tasks",
    description="AI-powered notes and task management",
    on_load=AppState.on_load
)

# Compile the app
if __name__ == "__main__":
    app.compile()