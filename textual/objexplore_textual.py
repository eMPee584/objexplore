from typing import Any, Optional, Type

import rich

import textual
import textual.app
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.driver import Driver
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Placeholder,
    Static,
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


class ObjectExplorer(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self, *args, obj, **kwargs):
        self.obj = obj
        self.selected_obj = obj

        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(classes="column"):
                tree = Tree(self.obj.__name__)
                # root_obj = tree.root.add(self.obj.__name__)
                for sub_obj in dir(self.obj):
                    tree.root.add_leaf(sub_obj)
                # foo = tree.root.add("foo", expand=False)
                # foo.add_leaf("bar")
                # foo.add_leaf("baz")
                yield tree

            with Vertical(classes="column"):
                # with console.capture() as capture:
                #     rich.inspect(self.selected_obj)

                yield Static(get_inspect(self.obj))

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

        # with self.suspend():
        #     breakpoint()
        #     print("hello")

        self.obj = getattr(self.obj, str(node.node.label))


if __name__ == "__main__":
    app = ObjectExplorer(obj=Button)
    app.run()
