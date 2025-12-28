from textual.app import App, ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import Input, Button, Label
from textual.screen import Screen

# You see, I was going to implement this into the socket program for visually appealing reasons, but i realized that I don't NEED it and that it's tedious work that does not HAVE to be done. 
#
# ^That^ being said, if anyone wants to contribute, feel free to implement this into both ser.py and cli.py.

class InputScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Container(
            Vertical(
                Label("Welcome", id="title"),
                Label("Please enter both fields to continue", id="subtitle"),

                Input(placeholder="IPv4 Address", id="input_one"),
                Input(placeholder="Port number", id="input_two"),

                Label("", id="error"),
                Button("Continue", id="continue_btn"),
                id="card",
            ),
            id="outer",
        )

    def on_mount(self) -> None:
        self.query_one("#input_one", Input).focus()

    def validate_and_continue(self) -> None:
        v1 = self.query_one("#input_one", Input).value.strip()
        v2 = self.query_one("#input_two", Input).value.strip()

        if v1 and v2:
            self.app.push_screen(SecondScreen())
        else:
            self.query_one("#error", Label).update("Both fields are required")

    def on_button_pressed(self) -> None:
        self.validate_and_continue()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.validate_and_continue()


class SecondScreen(Screen):
    BINDINGS = [
        ("ctrl+r", "restart", "Restart"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Vertical(
                Label("This is the second screen"),
                Label("Press Ctrl+R to restart", id="hint"),
            ),
            id="outer",
        )

    def action_restart(self) -> None:
        self.app.restart_flow()



class PrettyApp(App):
    CSS_PATH = "styles.css"

    def restart_flow(self) -> None:
        self.pop_screen()
        self.push_screen(InputScreen())

    def on_mount(self) -> None:
        self.push_screen(InputScreen())



if __name__ == "__main__":
    PrettyApp().run()

