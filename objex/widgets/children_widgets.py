from tracemalloc import start
from typing import List

import rich
import textual
from new_cached_object import NewCachedChildObject, NewCachedObject
from rapidfuzz import fuzz
from rich._inspect import Inspect
from rich.panel import Panel
from rich.pretty import Pretty as RichPretty
from rich.style import Style
from rich.text import Text
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input as TextualInput
from textual.widgets import Label, Pretty, Static
from widgets.preview import InspectedObjectWidget

console = rich.get_console()


class Input(TextualInput):
    BINDINGS = [("escape", "leave_focus")]

    def action_leave_focus(self):
        self.blur()

    def on_mount(self):
        self.styles.margin = (0, 0, 1, 0)


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

    def on_enter(self, event):
        self.app.query_one(InspectedObjectWidget).preview_object = self.cached_object

    def on_leave(self, event):
        self.app.query_one(InspectedObjectWidget).preview_object = None


class ChildrenWidget(Static):
    TOOLTIP_DELAY = 0.1

    search_query = reactive(default="", recompose=True)
    show_private = reactive(default=False, recompose=True)
    show_dunder = reactive(default=False, recompose=True)
    type_filters = reactive(default=[], recompose=True)
    search_help = reactive(default=False, recompose=True)
    fuzzy_search = reactive(default=True, recompose=True)

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
            yield ChildWidget(
                cached_object=cached_child,
            )

    def get_children(self):
        return [
            child
            for child in self.cached_object.cached_children
            if self.matches_search_query(child)
            and (self.show_private or not child.name.startswith("_"))
            and (self.show_dunder or not child.name.startswith("__"))
        ]

    def matches_search_query(self, child: NewCachedObject):
        # TODO special searching for iterables
        matches_name = self.search_query.lower() in child.name.lower()
        if not self.fuzzy_search or len(self.search_query) < 4:

            if not self.search_help:
                return matches_name
            else:
                return matches_name or (
                    self.search_query.lower() in child.docstring.lower()
                    if child.docstring is not None
                    else False
                )

        else:
            if self.search_query:
                matches_name = matches_name or (
                    fuzz.ratio(self.search_query.lower(), child.name.lower()) > 50
                )
                if not self.search_help:
                    return matches_name
                else:
                    return matches_name or (
                        fuzz.partial_ratio(
                            self.search_query.lower(), child.docstring.lower()
                        )
                        > 50
                        if child.docstring is not None
                        else False
                    )
            else:
                return True


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
