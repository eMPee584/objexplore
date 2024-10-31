import inspect
from typing import Any, List, Optional

import rich
from new_cached_object import NewCachedChildObject, NewCachedObject
from rich.console import Console
from rich.style import Style

import textual
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.driver import Driver
from textual.events import Enter, Leave
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header
from textual.widgets import Input as TextualInput
from textual.widgets import (
    Label,
    OptionList,
    Pretty,
    Static,
    Switch,
    TabbedContent,
    TabPane,
)
from textual.widgets.option_list import Option, Separator

console = rich.get_console()


def get_inspect(
    obj: Any,
    *,
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


class MyLabel(Static):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text

    def render(self):
        return self.text


class ChildWidget(Static):
    DEFAULT_CSS = """
    ChildWidget > MyLabel:hover {
        background: $primary-background-darken-1;
    }
    """

    def __init__(
        self,
        parent_cached_object: NewCachedObject,
        cached_child: NewCachedChildObject,
        *args,
        **kwargs,
    ):
        self.parent_cached_object = parent_cached_object
        self.cached_child = cached_child
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.height = "auto"

    def compose(self):
        yield MyLabel(self.cached_child.label)
        # actual_child_object = getattr(self.parent_object, self.child_label)

        # with Horizontal() as h:
        #     h.styles.height = "auto"
        #     with Vertical() as v:
        #         v.styles.height = "auto"
        #         v.styles.width = "25%"
        #         v.styles.align = ("right", "middle")
        #         v.styles.text_style = Style(bold=True, italic=True)
        #         label = Label(self.child_label)
        #         label.styles.margin = 1
        #         yield label

        #     with Vertical() as v:
        #         v.styles.height = "3"
        #         v.styles.border = ("round", "green")
        #         yield Static("hello")
        #         # pretty = Pretty(actual_child_object)
        #         # yield pretty


class ChildrenWidget(Static):
    DEFAULT_CSS = """
    ChildrenWidget > OptionList:focus > .option-list--option-highlighted {
        text-style: reverse
    }
    """

    BINDINGS = [
        ("j", "cursor_down"),
        ("k", "cursor_up"),
    ]

    search_query = reactive("", recompose=True)

    def __init__(
        self,
        parent_cached_object: NewCachedObject,
        cached_children: List[NewCachedChildObject],
        *args,
        **kwargs,
    ):
        self.parent_cached_object = parent_cached_object
        self.cached_children = cached_children
        super().__init__(*args, **kwargs)

    def compose(self):
        for cached_child in self.cached_children:
            if self.search_query.lower() in cached_child.label.lower():
                yield ChildWidget(
                    parent_cached_object=self.parent_cached_object,
                    cached_child=cached_child,
                )

        # yield OptionList(
        #     *[
        #         self.get_option_for_child(child_label)
        #         for child_label in self.child_labels
        #         if self.search_query.lower() in child_label.lower()
        #     ],
        #     wrap=False,
        # )


#     def action_cursor_down(self) -> None:
#         return self.query_one(OptionList).action_cursor_down()

#     def action_cursor_up(self) -> None:
#         return self.query_one(OptionList).action_cursor_up()

# def get_option_for_child(self, child_label):
#     child_object = getattr(self.parent_object, child_label)

#     if child_object is None:
#         return Option(f"[strike][dim]{child_label}[/]", id=child_label)

#     elif inspect.isclass(child_object):
#         return Option(f"[magenta]{child_label}[/]", id=child_label)

#     elif inspect.ismodule(child_object):
#         return Option(f"[blue]{child_label}[/]", id=child_label)

#     elif inspect.ismethod(child_object) or inspect.isfunction(child_object):
#         return Option(f"[cyan]{child_label}[/cyan]()", id=child_label)

#     elif isinstance(child_object, dict):
#         return Option("{**[cyan]" + child_label + "[/]}", id=child_label)

#     elif isinstance(child_object, bool):
#         color = "green" if child_object else "red"
#         return Option(
#             f"{child_label} = [{color}][i]{child_object}[/i][/{color}]",
#             id=child_label,
#         )

#     elif isinstance(child_object, str):
#         return Option(
#             f"{child_label} = [green][i]'{child_object}'[/i][/green]",
#             id=child_label,
#         )

#     elif isinstance(child_object, list):
#         return Option(
#             "[*" + f"[red]{child_label}[/red]" + "]",
#             id=child_label,
#         )

#     return Option(child_label, id=child_label)


class SearchableChildrenWidget(Static):

    def __init__(self, cached_obj, *args, **kwargs):
        self.cached_obj = cached_obj
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Input(placeholder="Search Attributes")
        with VerticalScroll():
            yield ChildrenWidget(
                parent_cached_object=self.cached_obj,
                cached_children=self.get_child_labels(),
            )

    @textual.on(Input.Changed)
    def update_search_query(self, event: Input.Changed):
        self.query_one(ChildrenWidget).search_query = event.value

    def get_child_labels(self):
        return []


class PublicChildrenWidget(SearchableChildrenWidget):
    def get_child_labels(self):
        return self.cached_obj.public_children
        # return [
        #     child_label
        #     for child_label in dir(self.cached_obj)
        #     if not child_label.startswith("_")
        # ]


class PrivateChildrenWidget(SearchableChildrenWidget):
    def get_child_labels(self):
        return self.cached_obj.private_children
        # return [
        #     child_label
        #     for child_label in dir(self.cached_obj)
        #     if child_label.startswith("_")
        # ]


class DirectoryWidget(Static):
    def __init__(self, cached_obj: NewCachedObject, *args, **kwargs):
        self.cached_obj = cached_obj
        super().__init__(*args, **kwargs)

    def compose(self):
        with TabbedContent():
            with TabPane("Public", id="public"):
                yield PublicChildrenWidget(cached_obj=self.cached_obj)

            with TabPane("Private", id="private"):
                yield PrivateChildrenWidget(cached_obj=self.cached_obj)


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
        if isinstance(self.selected_object, bool):
            with Horizontal():
                with Vertical():
                    p = Pretty(self.selected_object)
                    p.styles.border = ("round", "cyan")
                    p.border_title = "Value"
                    p.styles.border_title_color = "white"
                    p.styles.border_title_style = Style(italic=True)
                    yield p
                with Vertical():
                    yield Switch(self.selected_object)

        elif inspect.isclass(self.selected_object) or inspect.ismodule(
            self.selected_object
        ):
            yield Input(placeholder="Search Attributes")

            for child_label in dir(self.selected_object):
                yield ChildWidget(
                    parent_cached_object=self.selected_object, cached_child=child_label
                )


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
