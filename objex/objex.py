import rich
from new_cached_object import NewCachedObject
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, TabbedContent
from widgets.children_widgets import Input
from widgets.preview import InspectedObjectWidget, PreviewWidget
from widgets.search import SearchWidget


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
        super().__init__(*args, **kwargs)
        self.cached_object = NewCachedObject(obj)
        self.cached_object.cache_children()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="column") as v:
                v.styles.width = "30%"
                yield SearchWidget(cached_object=self.cached_object)

            with Vertical(classes="column") as v:
                yield PreviewWidget(cached_object=self.cached_object)

        yield Footer()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.app.dark = not self.app.dark

    def action_focus_search(self) -> None:
        """An action to toggle dark mode."""
        self.query_one(Input).focus()


def explore(obj=None):
    if obj is None:
        obj = globals()

    app = ObjectExplorer(obj=obj)
    app.run()


if __name__ == "__main__":
    import pandas

    explore(obj=pandas)
    # app = ObjectExplorer(obj=pandas)
    # # app = ObjectExplorer(obj=rich)
    # # app = ObjectExplorer(obj=console)
    # # app.run(inline=True)
    # app.run()
