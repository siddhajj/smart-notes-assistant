import pynecone as pc

class ViewNoteState(pc.State):
    note_id: str
    note_title: str = ""
    note_body: str = ""
    error_message: str = ""
    show_delete_dialog: bool = False

    @pc.var
    def get_note_id(self) -> str:
        return self.router.page.params.get("note_id", "")

    async def get_note(self):
        if not self.get_note_id:
            return
        try:
            response = await pc.api.get(f"/notes/{self.get_note_id}")
            if response.status_code == 200:
                note_data = response.json()
                self.note_title = note_data["title"]
                self.note_body = note_data["body"]
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to fetch note.")
                if response.status_code == 404:
                    return pc.redirect("/notes?error=Note not found")
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

def view_note():
    return pc.center(
        pc.vstack(
            pc.heading(ViewNoteState.note_title),
            pc.text(ViewNoteState.note_body),
            pc.cond(
                ViewNoteState.error_message != "",
                pc.text(ViewNoteState.error_message, color="red")
            ),
            pc.hstack(
                pc.link("Back to Notes", href="/notes"),
                pc.link("Edit Note", href=f"/notes/{ViewNoteState.get_note_id}/edit"),
                pc.button("Delete Note", on_click=ViewNoteState.toggle_delete_dialog),
            ),
            pc.cond(
                ViewNoteState.show_delete_dialog,
                pc.alert_dialog(
                    pc.alert_dialog_overlay(
                        pc.alert_dialog_content(
                            pc.alert_dialog_header("Confirm Deletion"),
                            pc.alert_dialog_body("Are you sure you want to delete this note? This action cannot be undone."),
                            pc.alert_dialog_footer(
                                pc.button("Cancel", on_click=ViewNoteState.toggle_delete_dialog),
                                pc.button("Delete", on_click=ViewNoteState.handle_delete_note, color_scheme="red"),
                            ),
                        )
                    )
                ),
            ),
        ),
        width="100vw",
        height="100vh",
        on_load=ViewNoteState.get_note
    )
