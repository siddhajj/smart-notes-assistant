import pynecone as pc

class RegisterState(pc.State):
    username: str
    email: str
    password: str
    error_message: str = ""

    def handle_register(self):
        # This will be replaced by actual API call
        if not self.username or not self.email or not self.password:
            self.error_message = "All fields are required."
            return
        print(f"Registering: {self.username}, {self.email}, {self.password}")
        self.error_message = ""
        return pc.redirect("/login")

def register():
    return pc.center(
        pc.vstack(
            pc.heading("Register"),
            pc.input(placeholder="Username", on_change=RegisterState.set_username),
            pc.input(placeholder="Email", on_change=RegisterState.set_email),
            pc.input(placeholder="Password", type_="password", on_change=RegisterState.set_password),
            pc.button("Register", on_click=RegisterState.handle_register),
            pc.cond(RegisterState.error_message != "", pc.text(RegisterState.error_message, color="red")),
            pc.link("Already have an account? Login", href="/login"),
        ),
        width="100vw",
        height="100vh",
    )
