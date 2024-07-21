import textual
from cached_object import CachedObject
from rich.style import Style
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input as TextualInput
from textual.widgets import Label, OptionList, Static, TabbedContent, TabPane


class ChildrenOptionList(Static):
    DEFAULT_CSS = """
    ChildrenWidget > OptionList:focus > .option-list--option-highlighted {
        text-style: reverse
    }
    """

    BINDINGS = [
        ("j", "cursor_down"),
        ("k", "cursor_up"),
        # ("escape", "leave_focus"),
    ]
    search_query = reactive("", recompose=True)

    def __init__(self, cached_object: "CachedObject", *args, **kwargs):
        self.options = cached_object
        super().__init__(*args, **kwargs)

    def compose(self):
        yield OptionList(*self.get_options())

    def action_cursor_down(self) -> None:
        return self.query_one(OptionList).action_cursor_down()

    def action_cursor_up(self) -> None:
        return self.query_one(OptionList).action_cursor_up()

    def get_options(self):
        return []

    # def action_leave_focus(self):
    #     self.query_one(OptionList).blur()


class Input(TextualInput):
    BINDINGS = [("escape", "leave_focus")]

    def action_leave_focus(self):
        self.blur()


class SearchableChildrenWidget(Static):

    def __init__(self, cached_object, *args, **kwargs):
        self.cached_object = cached_object
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Input(placeholder="Search Attributes")
        with VerticalScroll():
            yield ChildrenOptionList(cached_object=self.cached_object)

    @textual.on(Input.Changed)  # type: ignore
    def update_search_query(self, event: Input.Changed):
        self.query_one(ChildrenOptionList).search_query = event.value

    def get_options(self):
        return []


class PrivateChildrenOptionList(ChildrenOptionList):
    def get_options(self):
        return self.options.get_private_children_options(self.search_query)


class PrivateSearchableChildrenWidget(SearchableChildrenWidget):
    def compose(self):
        yield Input(placeholder="Search Attributes")
        with VerticalScroll():
            yield PrivateChildrenOptionList(cached_object=self.cached_object)


class PublicChildrenOptionList(ChildrenOptionList):
    def get_options(self):
        return self.options.get_public_children_options(self.search_query)


class PublicSearchableChildrenWidget(SearchableChildrenWidget):
    def compose(self):
        yield Input(placeholder="Search Attributes")
        with VerticalScroll():
            yield PublicChildrenOptionList(cached_object=self.cached_object)


class DirectoryWidget(Static):
    def __init__(self, cached_object: "CachedObject", *args, **kwargs):
        self.cached_object = cached_object
        super().__init__(*args, **kwargs)

    def compose(self):
        with TabbedContent():
            with TabPane("Public", id="public"):
                yield PublicSearchableChildrenWidget(cached_object=self.cached_object)

            with TabPane("Private", id="private"):
                yield PrivateSearchableChildrenWidget(cached_object=self.cached_object)


class ChildWidget(Static):
    DEFAULT_CSS = """
    ChildWidget > * > *:hover {
        background: $primary-background-darken-1;
    }
    """

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
            with Vertical() as v:
                v.styles.height = "auto"
                v.styles.width = "25%"
                v.styles.align = ("right", "middle")
                v.styles.text_style = Style(bold=True, italic=True)
                label = Label(self.child_label)
                label.styles.margin = 1
                yield label

            with Vertical() as v:
                v.styles.height = "3"
                v.styles.border = ("round", "green")
                yield Static("hello")
