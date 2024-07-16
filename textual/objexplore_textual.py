import inspect
from tkinter import Place
from typing import Any, Optional, Type

import rich

from textual import on
from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    Grid,
    Horizontal,
    ScrollableContainer,
    Vertical,
    VerticalScroll,
)
from textual.driver import Driver
from textual.events import Enter, Leave
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    Placeholder,
    Pretty,
    Rule,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)
from textual.widgets.option_list import Option, Separator

console = rich.get_console()


def get_inspect(
    obj: Any,
    *,
    console: Optional["Console"] = None,
    title: Optional[str] = None,
    help: bool = False,
    methods: bool = False,
    docs: bool = True,
    private: bool = False,
    dunder: bool = False,
    sort: bool = True,
    all: bool = False,
    value: bool = True,
):
    """Inspect any Python object.

    * inspect(<OBJECT>) to see summarized info.
    * inspect(<OBJECT>, methods=True) to see methods.
    * inspect(<OBJECT>, help=True) to see full (non-abbreviated) help.
    * inspect(<OBJECT>, private=True) to see private attributes (single underscore).
    * inspect(<OBJECT>, dunder=True) to see attributes beginning with double underscore.
    * inspect(<OBJECT>, all=True) to see all attributes.

    Args:
        obj (Any): An object to inspect.
        title (str, optional): Title to display over inspect result, or None use type. Defaults to None.
        help (bool, optional): Show full help text rather than just first paragraph. Defaults to False.
        methods (bool, optional): Enable inspection of callables. Defaults to False.
        docs (bool, optional): Also render doc strings. Defaults to True.
        private (bool, optional): Show private attributes (beginning with underscore). Defaults to False.
        dunder (bool, optional): Show attributes starting with double underscore. Defaults to False.
        sort (bool, optional): Sort attributes alphabetically. Defaults to True.
        all (bool, optional): Show all attributes. Defaults to False.
        value (bool, optional): Pretty print value. Defaults to True.
    """
    _console = console or rich.get_console()
    from rich._inspect import Inspect

    # Special case for inspect(inspect)
    is_inspect = obj is rich.inspect

    _inspect = Inspect(
        obj,
        title=title,
        help=is_inspect or help,
        methods=is_inspect or methods,
        docs=is_inspect or docs,
        private=private,
        dunder=dunder,
        sort=sort,
        all=all,
        value=value,
    )
    return _inspect


class InspectWidget(Static):
    def __init__(self, obj, **kwargs):
        self.obj = obj
        super().__init__(get_inspect(obj), **kwargs)

    def compose(self):
        yield Static(get_inspect(self.obj))


class ChildWidget(Static):
    DEFAULT_CSS = """
    Grid {
        grid-size: 2 1;
    }
    """

    def __init__(self, parent_object, child_label, *args, **kwargs):
        self.parent_object = parent_object
        self.child_label = child_label
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.height = "auto"

    def _on_enter(self, event: Enter) -> None:
        # self.original_background = self.styles.background
        # self.styles.background = "red"
        return super()._on_enter(event)

    def _on_leave(self, event: Leave) -> None:
        # self.styles.background = self.original_background
        return super()._on_leave(event)

    def compose(self):
        actual_child_object = getattr(self.parent_object, self.child_label)

        with Horizontal() as h:
            h.styles.height = "auto"
            label = Label(self.child_label)
            label.styles.padding = (0, 1)
            pretty = Pretty(type(actual_child_object))
            yield pretty

        # with Grid() as g:
        #     g.styles.height = "auto"
        #     yield Label(self.child_label)
        #     yield Pretty(type(actual_child_object))
        #     # yield Placeholder()
        #     # yield Placeholder()


from dataclasses import dataclass

from rich.console import Console, ConsoleOptions, RenderResult
from rich.pretty import Pretty as RichPretty
from rich.table import Table


@dataclass
class Student:
    label: str

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield f"[b]Label:[/b] #{self.label}"
        my_table = Table("Attribute", "Value")
        my_table.show_lines = False
        my_table.add_row("label", self.label)
        my_table.add_row("type", RichPretty(self.label))
        yield my_table


class ChildrenWidget(Static):
    search_query = reactive("", recompose=True)

    def __init__(self, parent_object, child_labels, *args, **kwargs):
        self.parent_object = parent_object
        self.child_labels = child_labels
        super().__init__(*args, **kwargs)

    def compose(self):

        # with ListView():
        #     for child_label in [
        #         child
        #         for child in self.child_labels
        #         if self.search_query.lower() in child.lower()
        #     ]:
        #         yield ListItem(
        #             ChildWidget(
        #                 parent_object=self.parent_object, child_label=child_label
        #             )
        #             # Static(child_label)
        #         )

        yield OptionList(
            *[
                # Option(f"[cyan]{child_label}[/]")
                self.get_option_for_child(child_label)
                for child_label in self.child_labels
                if self.search_query.lower() in child_label.lower()
            ]
        )

    def get_option_for_child(self, child_label):
        child_object = getattr(self.parent_object, child_label)

        if child_object is None:
            return Option(f"[strike][dim]{child_label}[/]")

        if inspect.isclass(child_object):
            return Option(f"[magenta]{child_label}[/]")

        if callable(child_object):
            return Option(f"[cyan][i]{child_label}[/cyan]()[/i]")

        if isinstance(child_object, dict):
            return Option("{**[cyan]" + child_label + "[/]}")

        return Option(child_label)


class MyInput(Input):
    BINDINGS = [
        (
            "escape",
            "leave_focus",
        )
    ]

    def action_leave_focus(self):
        self.blur()


class SearchableChildrenWidget(Static):

    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self):
        yield MyInput(placeholder="Search Attributes")
        with VerticalScroll():
            yield ChildrenWidget(
                parent_object=self.obj, child_labels=self.get_child_labels()
            )

    @on(Input.Changed)
    def update_search_query(self, event: Input.Changed):
        self.query_one(ChildrenWidget).search_query = event.value

    def get_child_labels(self):
        return []


class PublicChildrenWidget(SearchableChildrenWidget):
    def get_child_labels(self):
        return [
            child_label
            for child_label in dir(self.obj)
            if not child_label.startswith("_")
        ]


class PrivateChildrenWidget(SearchableChildrenWidget):
    def get_child_labels(self):
        return [
            child_label for child_label in dir(self.obj) if child_label.startswith("_")
        ]


class DirectoryWidget(Static):

    BINDINGS = [
        ("[", "toggle_public_private"),
        ("]", "toggle_public_private"),
        ("/", "focus_search"),
    ]

    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self):
        with TabbedContent():
            with TabPane("Public", id="public"):
                yield PublicChildrenWidget(obj=self.obj)
            with TabPane("Private", id="private"):
                yield PrivateChildrenWidget(obj=self.obj)

    def action_toggle_public_private(self):
        tabbed_content = self.query_one(TabbedContent)

        if tabbed_content.active == "public":
            tabbed_content.active = "private"
        else:
            tabbed_content.active = "public"

    def action_focus_search(self):
        self.query_one(TabbedContent).active_pane.query_one(Input).focus()


class ObjectExplorer(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self, *args, obj, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="column"):
                yield DirectoryWidget(obj=self.obj)

            with Vertical(classes="column"):
                yield Static("hello")

        yield Footer()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = ObjectExplorer(obj=console)
    app.run()
