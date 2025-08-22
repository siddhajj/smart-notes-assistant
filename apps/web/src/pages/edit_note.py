import pynecone as pc

class EditNoteState(pc.State):
    note_id: str
    title: str
    body: str
    error_message: str = ""
    show_delete_dialog: bool = False

    @pc.var
    def get_note_id(self) -> str:
        return self.router.page.params.get("note_id", "")

    async def get_note_details(self):
        if not self.get_note_id:
            return
        try:
            response = await pc.api.get(f"/notes/{self.get_note_id}")
            if response.status_code == 200:
                note_data = response.json()
                self.title = note_data["title"]
                self.body = note_data["body"]
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to fetch note details.")
                if response.status_code == 404:
                    return pc.redirect("/notes?error=Note not found")
        except Exception as e:
            self.error_message = f"Network error: {e}"

    async def handle_update_note(self):
        try:
            response = await pc.api.put(
                f"/notes/{self.get_note_id}",
                {
                    "title": self.title,
                    "body": self.body
                }
            )
            if response.status_code == 200:
                return pc.redirect(f"/notes/{self.get_note_id}") # Redirect to view note on success
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to update note.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

    def toggle_delete_dialog(self):
        self.show_delete_dialog = not self.show_delete_dialog

    async def handle_delete_note(self):
        try:
            response = await pc.api.delete(f"/notes/{self.get_note_id}")
            if response.status_code == 204:
                return pc.redirect("/notes") # Redirect to notes list on success
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to delete note.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def edit_note():
    return pc.center(
        pc.vstack(
            pc.heading("Edit Note"),
            pc.input(placeholder="Title", value=EditNoteState.title, on_change=EditNoteState.set_title),
            pc.text_area(placeholder="Body", value=EditNoteState.body, on_change=EditNoteState.set_body),
            pc.button("Update Note", on_click=EditNoteState.handle_update_note),
            pc.cond(EditNoteState.error_message != "", pc.text(EditNoteState.error_message, color="red")),
            pc.hstack(
                pc.link("Cancel", href=f"/notes/{EditNoteState.get_note_id}"),
                pc.button("Delete Note", on_click=EditNoteState.toggle_delete_dialog),
            ),
            pc.cond(
                EditNoteState.show_delete_dialog,
                pc.alert_dialog(
                    pc.alert_dialog_overlay(
                        pc.alert_dialog_content(
                            pc.alert_dialog_header("Confirm Deletion"),
                            pc.alert_dialog_body("Are you sure you want to delete this note? This action cannot be undone."),
                            pc.alert_dialog_footer(
                                pc.button("Cancel", on_click=EditNoteState.toggle_delete_dialog),
                                pc.button("Delete", on_click=EditNoteState.handle_delete_note, color_scheme="red"),
                            ),
                        )
                    )
                ),
            ),
        ),
        width="100vw",
        height="100vh",
        on_load=EditNoteState.get_note_details
    )
