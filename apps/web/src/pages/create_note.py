import pynecone as pc

class CreateNoteState(pc.State):
    title: str
    body: str
    error_message: str = ""

    async def handle_create_note(self):
        try:
            response = await pc.api.post(
                "/notes",
                {
                    "title": self.title,
                    "body": self.body
                }
            )
            if response.status_code == 201:
                return pc.redirect("/notes") # Redirect to notes list on success
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to create note.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def create_note():
    return pc.center(
        pc.vstack(
            pc.heading("Create New Note"),
            pc.input(placeholder="Title", on_change=CreateNoteState.set_title),
            pc.text_area(placeholder="Body", on_change=CreateNoteState.set_body),
            pc.button("Create Note", on_click=CreateNoteState.handle_create_note),
            pc.cond(CreateNoteState.error_message != "", pc.text(CreateNoteState.error_message, color="red")),
            pc.link("Back to Notes", href="/notes"),
        ),
        width="100vw",
        height="100vh",
    )