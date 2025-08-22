import reflex as rx
from ..state.main_state import MainState
from .auth_modal import AuthState

def header() -> rx.Component:
    """Main application header"""
    return rx.box(
        rx.hstack(
            # Logo/Title
            rx.hstack(
                rx.icon("book-open", size=32, color="blue.600"),
                rx.heading(
                    "Smart Notes Assistant",
                    size="7",
                    color="gray.800",
                    weight="bold"
                ),
                spacing="3",
                align="center"
            ),
            
            rx.spacer(),
            
            # User section
            rx.cond(
                MainState.is_authenticated,
                # Authenticated user
                rx.hstack(
                    rx.text(
                        f"Welcome, {MainState.username}",
                        font_size="1rem",
                        color="gray.700"
                    ),
                    rx.button(
                        rx.icon("log-out", size=16),
                        "Logout",
                        on_click=MainState.logout,
                        variant="outline",
                        color_scheme="red",
                        size="sm"
                    ),
                    spacing="4",
                    align="center"
                ),
                # Not authenticated
                rx.hstack(
                    rx.button(
                        "Login",
                        on_click=AuthState.show_login_modal,
                        color_scheme="blue",
                        size="sm"
                    ),
                    rx.button(
                        "Sign Up",
                        on_click=AuthState.show_register_modal,
                        variant="outline",
                        color_scheme="blue",
                        size="sm"
                    ),
                    spacing="2"
                )
            ),
            
            width="100%",
            align="center",
            justify="between"
        ),
        
        width="100%",
        padding="1rem 2rem",
        border_bottom="1px solid var(--chakra-colors-gray-200)",
        background="white",
        position="sticky",
        top="0",
        z_index="100",
        box_shadow="sm"
    )