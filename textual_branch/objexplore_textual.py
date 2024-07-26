import inspect
from typing import List, Optional

import rich
from cached_object import CachedObject
from common_widgets import Input
from directory_panel import DirectoryWidget
from inspect_panel import InspectedObjectWidget, get_inspect
from rich.console import Console
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, OptionList, TabbedContent

console = rich.get_console()


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
        ("l", "enter_object"),
    ]

    def __init__(self, *args, obj, **kwargs):
        self.obj = obj

        frame = inspect.currentframe()
        label = frame.f_back.f_code.co_names[1]  # type: ignore

        self.cached_object = CachedObject(obj, label=label)
        self.cached_object.cache()
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="column") as v:
                v.styles.width = "30%"
                yield DirectoryWidget(cached_object=self.cached_object)

            with Vertical(classes="column"):
                yield InspectedObjectWidget()

        yield Footer()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_option_list_option_highlighted(self, event):
        inspector = self.query_one(InspectedObjectWidget)
        inspector.cached_object = self.cached_object.cached_children[event.option.id]  # type: ignore

    def action_enter_object(self):
        option_list = (
            self.query_one(DirectoryWidget)
            .query_one(TabbedContent)
            .active_pane.query_one(OptionList)
        )

        with self.app.suspend():
            breakpoint()

        self.cached_object = self.cached_object.cached_children[option_list.get_option_at_index(option_list.highlighted).id]  # type: ignore
        self.cached_object.cache()

    def action_toggle_public_private(self):
        tabbed_content = self.query_one(TabbedContent)

        if tabbed_content.active == "public":
            tabbed_content.active = "private"
        else:
            tabbed_content.active = "public"

    def action_focus_search(self):
        self.query_one(TabbedContent).active_pane.query_one(Input).focus()

    def action_cursor_down(self) -> None:
        option_list: OptionList = self.query_one(DirectoryWidget).query_one(TabbedContent).active_pane.query_one(OptionList)  # type: ignore
        option_list.focus()

    def action_cursor_up(self) -> None:
        option_list: OptionList = self.query_one(DirectoryWidget).query_one(TabbedContent).active_pane.query_one(OptionList)  # type: ignore
        option_list.focus()


if __name__ == "__main__":
    import pandas

    # app = ObjectExplorer(obj=pandas)
    app = ObjectExplorer(obj=rich)
    # app = ObjectExplorer(obj=console)
    # app.run(inline=True)
    app.run()
    # app.run(inline=True)
    app.run()
