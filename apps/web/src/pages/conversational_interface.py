import pynecone as pc

class ConversationalInterfaceState(pc.State):
    user_input: str = ""
    ai_response: str = ""
    error_message: str = ""

    async def handle_query(self):
        try:
            response = await pc.api.post(
                "/ai/query",
                {
                    "query": self.user_input
                }
            )
            if response.status_code == 200:
                response_data = response.json()
                if "notes" in response_data:
                    self.ai_response = "Found notes: " + ", ".join([note["title"] for note in response_data["notes"]])
                elif "tasks" in response_data:
                    self.ai_response = "Found tasks: " + ", ".join([task["description"] for task in response_data["tasks"]])
                else:
                    self.ai_response = response_data.get("message", "")
            else:
                error_data = response.json()
                self.error_message = error_data.get("detail", "Failed to get AI response.")
        except Exception as e:
            self.error_message = f"Network error: {e}"

def conversational_interface():
    return pc.center(
        pc.vstack(
            pc.heading("AI Assistant"),
            pc.text_area(placeholder="Type your command here...", on_change=ConversationalInterfaceState.set_user_input),
            pc.button("Send", on_click=ConversationalInterfaceState.handle_query),
            pc.cond(ConversationalInterfaceState.error_message != "", pc.text(ConversationalInterfaceState.error_message, color="red")),
            pc.cond(ConversationalInterfaceState.ai_response != "", pc.text(ConversationalInterfaceState.ai_response, color="green")),
        ),
        width="100vw",
        height="100vh",
    )