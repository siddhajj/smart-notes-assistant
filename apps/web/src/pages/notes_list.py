import pynecone as pc

class NotesListState(pc.State):
    notes: list = []
    error_message: str = ""

    async def get_notes(self):
        try:
            response = await pc.api.get("/notes")
            if response.status_code == 200:
                self.notes = response.json()
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to fetch notes.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def notes_list():
    return pc.center(
        pc.vstack(
            pc.heading("My Notes"),
            pc.cond(
                NotesListState.error_message != "",
                pc.text(NotesListState.error_message, color="red")
            ),
            pc.cond(
                len(NotesListState.notes) == 0,
                pc.text("No notes found. Create one!"),
                pc.foreach(
                    NotesListState.notes,
                    lambda note: pc.box(
                        pc.text(note["title"]),
                        pc.link("View", href=f"/notes/{note["id"]}"),
                        border_width="1px",
                        padding="10px",
                        margin_y="5px",
                        width="100%"
                    )
                )
            ),
            pc.link("Create New Note", href="/create_note"),
        ),
        width="100vw",
        height="100vh",
    )
