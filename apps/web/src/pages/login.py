import pynecone as pc

class LoginState(pc.State):
    email: str
    password: str
    error_message: str = ""

    def handle_login(self):
        # This will be replaced by actual API call
        if not self.email or not self.password:
            self.error_message = "Both fields are required."
            return
        print(f"Logging in: {self.email}, {self.password}")
        self.error_message = ""
        return pc.redirect("/") # Redirect to home on success

def login():
    return pc.center(
        pc.vstack(
            pc.heading("Login"),
            pc.input(placeholder="Email", on_change=LoginState.set_email),
            pc.input(placeholder="Password", type_="password", on_change=LoginState.set_password),
            pc.button("Login", on_click=LoginState.handle_login),
            pc.cond(LoginState.error_message != "", pc.text(LoginState.error_message, color="red")),
            pc.link("Don't have an account? Register", href="/register"),
        ),
        width="100vw",
        height="100vh",
    )
