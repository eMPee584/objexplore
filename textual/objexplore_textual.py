from typing import Any, Optional, Type

import rich

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.driver import Driver
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Placeholder,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

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
    def __init__(self, parent_object, child_label, *args, **kwargs):
        self.parent_object = parent_object
        self.child_label = child_label
        super().__init__(*args, **kwargs)

    def compose(self):
        actual_child_object = getattr(self.parent_object, self.child_label)

        yield Label(str(self.child_label))


class Name(Static):

    who = reactive("world")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.who = "world"

    def render(self):
        return f"Hello, {self.who}!"


class ChildrenWidget(Static):
    search_query = reactive("", recompose=True)

    def __init__(self, parent_object, child_labels, *args, **kwargs):
        self.parent_object = parent_object
        self.children_widgets = child_labels
        super().__init__(*args, **kwargs)

    def compose(self):
        with ScrollableContainer():
            for child_label in [
                child
                for child in self.children_widgets
                if self.search_query.lower() in child.lower()
            ]:
                yield ChildWidget(
                    parent_object=self.parent_object, child_label=child_label
                )


class SearchableChildrenWidget(Static):

    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self):
        with Vertical():
            yield Input(placeholder="Search Attributes")
            yield Static()
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
    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self):
        with TabbedContent():
            with TabPane("Public", id="public"):
                yield PublicChildrenWidget(obj=self.obj)
            with TabPane("Private", id="private"):
                yield PrivateChildrenWidget(obj=self.obj)

    # @on(Input.Changed)
    # def update_search_query(self, event: Input.Changed):
    #     active_tab = self.query_one(TabbedContent).active

    #     if active_tab == "public":
    #         self.query_one(PublicChildrenWidget).search_query = event.value

    #     elif active_tab == "private":
    #         self.query_one(PrivateChildrenWidget).search_query = event.value


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
                yield Static("Test")

        yield Footer()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_tree_node_selected(self, node):
        if node.node.is_root:
            return

        try:
            self.obj = getattr(self.obj, str(node.node.label))
        except:
            with self.suspend():
                breakpoint()
                print("hello")


if __name__ == "__main__":
    app = ObjectExplorer(obj=console)
    app.run()
