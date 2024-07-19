import inspect
from typing import Any, Optional, Type

import rich
from rich.style import Style

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
from textual.widgets import Button, Footer, Header
from textual.widgets import Input as TextualInput
from textual.widgets import (
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


class Input(TextualInput):
    BINDINGS = [("escape", "leave_focus")]

    def action_leave_focus(self):
        self.blur()


class InspectWidget(Static):
    def __init__(self, obj, **kwargs):
        self.obj = obj
        super().__init__(get_inspect(obj), **kwargs)

    def compose(self):
        yield Static(get_inspect(self.obj, all=True))


class ChildWidget(Static):
    def __init__(self, parent_object, child_label, *args, **kwargs):
        self.parent_object = parent_object
        self.child_label = child_label
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.height = "auto"

    def compose(self):
        actual_child_object = getattr(self.parent_object, self.child_label)

        with Horizontal() as h:
            h.styles.height = "auto"
            label = Label(self.child_label)
            label.styles.padding = (0, 1)
            pretty = Pretty(type(actual_child_object))
            yield pretty


class ChildrenWidget(Static):

    BINDINGS = [
        ("j", "cursor_down"),
        ("k", "cursor_up"),
    ]

    search_query = reactive("", recompose=True)

    def __init__(self, parent_object, child_labels, *args, **kwargs):
        self.parent_object = parent_object
        self.child_labels = child_labels
        super().__init__(*args, **kwargs)

    def compose(self):
        yield OptionList(
            *[
                self.get_option_for_child(child_label)
                for child_label in self.child_labels
                if self.search_query.lower() in child_label.lower()
            ],
            wrap=False,
        )

    def action_cursor_down(self) -> None:
        return self.query_one(OptionList).action_cursor_down()

    def action_cursor_up(self) -> None:
        return self.query_one(OptionList).action_cursor_up()

    def get_option_for_child(self, child_label):
        child_object = getattr(self.parent_object, child_label)

        if child_object is None:
            return Option(f"[strike][dim]{child_label}[/]", id=child_label)

        elif inspect.isclass(child_object):
            return Option(f"[magenta]{child_label}[/]", id=child_label)

        elif inspect.ismodule(child_object):
            return Option(f"[blue]{child_label}[/]", id=child_label)

        elif inspect.ismethod(child_object) or inspect.isfunction(child_object):
            return Option(f"[cyan]{child_label}[/cyan]()", id=child_label)

        elif isinstance(child_object, dict):
            return Option("{**[cyan]" + child_label + "[/]}", id=child_label)

        elif isinstance(child_object, bool):
            color = "green" if child_object else "red"
            return Option(
                f"{child_label} = [{color}][i]{child_object}[/i][/{color}]",
                id=child_label,
            )

        elif isinstance(child_object, str):
            return Option(
                f"{child_label} = [green][i]'{child_object}'[/i][/green]",
                id=child_label,
            )

        elif isinstance(child_object, list):
            return Option(
                "[*" + f"[red]{child_label}[/red]" + "]",
                id=child_label,
            )

        # else:
        #     with self.app.suspend():
        #         breakpoint()
        #         pass

        return Option(child_label, id=child_label)


class SearchableChildrenWidget(Static):

    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Input(placeholder="Search Attributes")
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
    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self):
        with TabbedContent():
            with TabPane("Public", id="public"):
                yield PublicChildrenWidget(obj=self.obj)

            with TabPane("Private", id="private"):
                yield PrivateChildrenWidget(obj=self.obj)


class DocstringWidget(Static):
    DEFAULT_CSS = """
    DocstringWidget:hover {
        background: $primary-background-darken-1;
    }
    """

    def __init__(self, selected_object, *args, **kwargs):
        self.selected_object = selected_object
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.border = ("round", "green")
        self.border_title = "docstring"
        self.styles.border_title_style = Style(italic=True, color="white")

    def render(self):
        docstring = inspect.getdoc(self.selected_object) or "None"
        return docstring


class PreviewWidget(Static):
    def __init__(self, selected_object, *args, **kwargs):
        self.selected_object = selected_object
        super().__init__(*args, **kwargs)

    def compose(self):
        yield InspectWidget(self.selected_object)

        # if inspect.ismodule(self.selected_object):
        #     yield InspectWidget(self.selected_object)
        # else:
        #     yield Pretty(self.selected_object)


class InspectedObjectWidget(Static):
    DEFAULT_CSS = """
    #pretty {
        background: $primary-background-darken-1;
        border: wide black;
    }
    """
    selected_object_label = reactive("")
    selected_object = reactive(None, recompose=True)

    def compose(self):
        with Horizontal() as h:
            h.styles.height = "3"
            with Vertical():
                label = Label(self.selected_object_label)
                label.styles.border = ("round", "cyan")
                label.border_title = "Name"
                label.styles.border_title_color = "white"
                label.styles.border_title_style = Style(italic=True)
                label.styles.width = "100%"
                yield label

            with Vertical():
                _type = Pretty(type(self.selected_object))
                _type.styles.border = ("round", "cyan")
                _type.border_title = "Type"
                _type.styles.border_title_color = "white"
                _type.styles.border_title_style = Style(italic=True)
                yield _type

        with VerticalScroll():
            yield PreviewWidget(selected_object=self.selected_object)
            # yield DocstringWidget(selected_object=self.selected_object)


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
        self.obj = obj
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(classes="column") as v:
                v.styles.width = "30%"
                yield DirectoryWidget(obj=self.obj)

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
        inspector.selected_object_label = event.option.id
        inspector.selected_object = getattr(self.obj, event.option.id)

    def action_toggle_public_private(self):
        tabbed_content = self.query_one(TabbedContent)

        if tabbed_content.active == "public":
            tabbed_content.active = "private"
        else:
            tabbed_content.active = "public"

    def action_focus_search(self):
        self.query_one(TabbedContent).active_pane.query_one(Input).focus()

    def action_cursor_down(self) -> None:
        # return self.query_one(ChildrenWidget).action_cursor_down()
        self.query_one(TabbedContent).active_pane.query_one(
            OptionList
        ).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(TabbedContent).active_pane.query_one(
            OptionList
        ).action_cursor_down()


if __name__ == "__main__":
    import pandas

    # app = ObjectExplorer(obj=pandas)
    app = ObjectExplorer(obj=rich)
    # app = ObjectExplorer(obj=console)
    # app.run(inline=True)
    app.run()
