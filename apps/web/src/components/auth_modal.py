import reflex as rx
from typing import Dict, Any

class AuthState(rx.State):
    """State for authentication modal"""
    show_auth_modal: bool = False
    auth_mode: str = "login"  # "login" or "register"
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    auth_error: str = ""
    is_loading: bool = False
    
    def show_login_modal(self):
        """Show login modal"""
        self.auth_mode = "login"
        self.show_auth_modal = True
        self._clear_form()
    
    def show_register_modal(self):
        """Show register modal"""
        self.auth_mode = "register"
        self.show_auth_modal = True
        self._clear_form()
    
    def close_auth_modal(self):
        """Close authentication modal"""
        self.show_auth_modal = False
        self._clear_form()
    
    def switch_to_register(self):
        """Switch from login to register"""
        self.auth_mode = "register"
        self._clear_form()
    
    def switch_to_login(self):
        """Switch from register to login"""
        self.auth_mode = "login"
        self._clear_form()
    
    def _clear_form(self):
        """Clear form fields and errors"""
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.auth_error = ""
        self.is_loading = False
    
    async def handle_login(self):
        """Handle login submission"""
        if not self.username or not self.password:
            self.auth_error = "Please fill in all fields"
            return
        
        self.is_loading = True
        self.auth_error = ""
        
        try:
            # TODO: Implement actual login API call
            # For now, just simulate success
            await rx.sleep(1)  # Simulate API call
            
            # Mock successful login
            if self.username and self.password:
                self.show_auth_modal = False
                self._clear_form()
                # TODO: Set authentication state in main app
                return rx.toast.success("Login successful!")
            else:
                self.auth_error = "Invalid credentials"
        
        except Exception as e:
            self.auth_error = f"Login failed: {str(e)}"
        
        finally:
            self.is_loading = False
    
    async def handle_register(self):
        """Handle registration submission"""
        if not self.username or not self.email or not self.password or not self.confirm_password:
            self.auth_error = "Please fill in all fields"
            return
        
        if self.password != self.confirm_password:
            self.auth_error = "Passwords do not match"
            return
        
        if len(self.password) < 6:
            self.auth_error = "Password must be at least 6 characters"
            return
        
        self.is_loading = True
        self.auth_error = ""
        
        try:
            # TODO: Implement actual registration API call
            # For now, just simulate success
            await rx.sleep(1)  # Simulate API call
            
            # Mock successful registration
            self.show_auth_modal = False
            self._clear_form()
            return rx.toast.success("Registration successful! Please log in.")
        
        except Exception as e:
            self.auth_error = f"Registration failed: {str(e)}"
        
        finally:
            self.is_loading = False

def login_form() -> rx.Component:
    """Login form component"""
    return rx.vstack(
        rx.heading("Login", size="6", margin_bottom="1rem"),
        rx.input(
            placeholder="Username",
            value=AuthState.username,
            on_change=AuthState.set_username,
            width="100%",
            margin_bottom="0.5rem"
        ),
        rx.input(
            placeholder="Password",
            type="password",
            value=AuthState.password,
            on_change=AuthState.set_password,
            width="100%",
            margin_bottom="1rem"
        ),
        rx.cond(
            AuthState.auth_error,
            rx.text(
                AuthState.auth_error,
                color="red",
                font_size="0.9rem",
                margin_bottom="0.5rem"
            )
        ),
        rx.hstack(
            rx.button(
                "Login",
                on_click=AuthState.handle_login,
                loading=AuthState.is_loading,
                width="100%",
                color_scheme="blue"
            ),
            width="100%",
            margin_bottom="1rem"
        ),
        rx.hstack(
            rx.text("Don't have an account?", font_size="0.9rem"),
            rx.button(
                "Sign up",
                variant="ghost",
                on_click=AuthState.switch_to_register,
                font_size="0.9rem",
                padding="0"
            ),
            justify="center",
            width="100%"
        ),
        width="100%",
        spacing="2"
    )

def register_form() -> rx.Component:
    """Register form component"""
    return rx.vstack(
        rx.heading("Create Account", size="6", margin_bottom="1rem"),
        rx.input(
            placeholder="Username",
            value=AuthState.username,
            on_change=AuthState.set_username,
            width="100%",
            margin_bottom="0.5rem"
        ),
        rx.input(
            placeholder="Email",
            type="email",
            value=AuthState.email,
            on_change=AuthState.set_email,
            width="100%",
            margin_bottom="0.5rem"
        ),
        rx.input(
            placeholder="Password",
            type="password",
            value=AuthState.password,
            on_change=AuthState.set_password,
            width="100%",
            margin_bottom="0.5rem"
        ),
        rx.input(
            placeholder="Confirm Password",
            type="password",
            value=AuthState.confirm_password,
            on_change=AuthState.set_confirm_password,
            width="100%",
            margin_bottom="1rem"
        ),
        rx.cond(
            AuthState.auth_error,
            rx.text(
                AuthState.auth_error,
                color="red",
                font_size="0.9rem",
                margin_bottom="0.5rem"
            )
        ),
        rx.hstack(
            rx.button(
                "Create Account",
                on_click=AuthState.handle_register,
                loading=AuthState.is_loading,
                width="100%",
                color_scheme="green"
            ),
            width="100%",
            margin_bottom="1rem"
        ),
        rx.hstack(
            rx.text("Already have an account?", font_size="0.9rem"),
            rx.button(
                "Sign in",
                variant="ghost",
                on_click=AuthState.switch_to_login,
                font_size="0.9rem",
                padding="0"
            ),
            justify="center",
            width="100%"
        ),
        width="100%",
        spacing="2"
    )

def auth_modal() -> rx.Component:
    """Authentication modal component"""
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.modal_close_button()
                ),
                rx.modal_body(
                    rx.cond(
                        AuthState.auth_mode == "login",
                        login_form(),
                        register_form()
                    ),
                    padding="2rem"
                ),
                max_width="400px",
                margin="auto"
            )
        ),
        is_open=AuthState.show_auth_modal,
        on_close=AuthState.close_auth_modal
    )