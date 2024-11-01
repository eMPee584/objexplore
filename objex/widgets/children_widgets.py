from typing import List

import rich
import textual
from new_cached_object import NewCachedChildObject, NewCachedObject
from rich.panel import Panel
from rich.pretty import Pretty as RichPretty
from rich.text import Text
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input as TextualInput
from textual.widgets import Label, Pretty, Static
from widgets.preview_widgets import InspectedObjectWidget

console = rich.get_console()


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
        parent_cached_object: NewCachedObject,
        cached_child: NewCachedChildObject,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent_cached_object = parent_cached_object
        self.cached_child = cached_child

    def on_mount(self):
        self.styles.height = "auto"
        style_color = self.cached_child.style_color
        self.styles.border = ("round", style_color)
        self.border_title = self.cached_child.title
        self.border_subtitle = self.cached_child.subtitle

    def render(self) -> Text | RichPretty:
        str_repr = self.cached_child.str_repr
        if console.measure(str_repr).minimum > console.width * 0.3:
            return "{...}"
        else:
            return str_repr

    def on_enter(self):
        self.cached_child.cache()
        self.app.query_one(selector=InspectedObjectWidget).selected_object = (
            self.cached_child
        )


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

    search_query = reactive(default="", recompose=True)

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
            if self.search_query.lower() in cached_child.name.lower():
                yield ChildWidget(
                    parent_cached_object=self.parent_cached_object,
                    cached_child=cached_child,
                )


class Input(TextualInput):
    BINDINGS = [("escape", "leave_focus")]

    def action_leave_focus(self):
        self.blur()


class SearchableChildrenWidget(Static):

    def __init__(self, cached_obj, *args, **kwargs):
        self.cached_obj = cached_obj
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Input(placeholder="Search Attributes")
        yield Label()
        with VerticalScroll() as v:
            yield ChildrenWidget(
                parent_cached_object=self.cached_obj,
                cached_children=self.get_child_labels(),
            )

    @textual.on(message_type=Input.Changed)
    def update_search_query(self, event: Input.Changed):
        self.query_one(selector=ChildrenWidget).search_query = event.value

    def get_child_labels(self):
        return []


class PublicChildrenWidget(SearchableChildrenWidget):
    def get_child_labels(self):
        return self.cached_obj.public_children


class PrivateChildrenWidget(SearchableChildrenWidget):
    def get_child_labels(self):
        return self.cached_obj.private_children
