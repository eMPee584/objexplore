import rich
from new_cached_object import NewCachedObject
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, TabbedContent
from widgets.directory_widget import DirectoryWidget
from widgets.preview_widgets import InspectedObjectWidget


class ObjectExplorer(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("[", "toggle_public_private"),
        ("]", "toggle_public_private"),
        ("/", "focus_search", "Search"),
        ("j", "cursor_down"),
        ("k", "cursor_up"),
    ]

    def __init__(self, *args, obj, **kwargs):
        self.cached_obj = NewCachedObject(obj)
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="column") as v:
                v.styles.width = "30%"
                yield DirectoryWidget(cached_obj=self.cached_obj)

            with Vertical(classes="column") as v:
                yield InspectedObjectWidget()

        yield Footer()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.app.dark = not self.app.dark

    def action_toggle_public_private(self):
        tabbed_content = self.query_one(selector=TabbedContent)

        if tabbed_content.active == "public":
            tabbed_content.active = "private"
        else:
            tabbed_content.active = "public"


#     def action_cursor_down(self) -> None:
#         self.query_one(TabbedContent).active_pane.query_one(
#             OptionList
#         ).action_cursor_down()

#     def action_cursor_up(self) -> None:
#         self.query_one(TabbedContent).active_pane.query_one(
#             OptionList
#         ).action_cursor_down()


if __name__ == "__main__":
    import pandas

    # app = ObjectExplorer(obj=pandas)
    app = ObjectExplorer(obj=rich)
    # app = ObjectExplorer(obj=console)
    # app.run(inline=True)
    app.run()
