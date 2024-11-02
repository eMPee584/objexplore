from tracemalloc import start
from typing import List

import rich
import textual
from new_cached_object import NewCachedChildObject, NewCachedObject
from rich._inspect import Inspect
from rich.panel import Panel
from rich.pretty import Pretty as RichPretty
from rich.style import Style
from rich.text import Text
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input as TextualInput
from textual.widgets import Label, Pretty, Static
from widgets.preview_widgets import InspectedObjectWidget

console = rich.get_console()


class Input(TextualInput):
    BINDINGS = [("escape", "leave_focus")]

    def action_leave_focus(self):
        self.blur()


class ChildWidget(Static):
    DEFAULT_CSS = """
    ChildWidget {
        max-height: 3;

        & :hover {
            background: $primary-background-darken-1;
        }
    }
    """

    def __init__(
        self,
        cached_object: NewCachedObject,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def on_mount(self):
        self.styles.height = "auto"
        style_color = self.cached_object.style_color
        self.styles.border = ("round", style_color)
        self.border_title = self.cached_object.title
        self.border_subtitle = self.cached_object.subtitle

    def render(self):
        str_repr = self.cached_object.str_repr
        if (
            isinstance(self.cached_object.obj, dict)
            and console.measure(str_repr).minimum > console.width * 0.3
        ):
            return "{...}"
        else:
            return str_repr


class ChildrenWidget(Static):
    TOOLTIP_DELAY = 0.1

    search_query = reactive(default="", recompose=True)
    show_private = reactive(default=False, recompose=True)
    show_dunder = reactive(default=False, recompose=True)
    type_filters = reactive(default=[], recompose=True)

    BINDINGS = [
        ("j", "cursor_down"),
        ("k", "cursor_up"),
    ]

    def __init__(
        self,
        cached_object: NewCachedObject,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def compose(self):
        for cached_child in self.get_children():
            c = ChildWidget(
                cached_object=cached_child,
            )
            # c.tooltip = Inspect(self.cached_object.obj)
            c.tooltip = Panel(
                "hello",
                height=6,
            )
            yield c

    def get_children(self):
        return [
            child
            for child in self.cached_object.cached_children
            if self.search_query.lower() in child.name.lower()
            and (self.show_private or not child.name.startswith("_"))
            and (self.show_dunder or not child.name.startswith("__"))
        ]
        
    @textual.on(ChildWidget.Enter)


class SearchableChildrenWidget(Static):

    def __init__(self, cached_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def compose(self):
        yield Input(placeholder="Search Attributes")
        with VerticalScroll() as v:
            yield ChildrenWidget(cached_object=self.cached_object)

    @textual.on(message_type=Input.Changed)
    def update_search_query(self, event: Input.Changed):
        self.query_one(selector=ChildrenWidget).search_query = event.value
