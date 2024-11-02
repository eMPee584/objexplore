import textual
from new_cached_object import NewCachedObject
from rich.text import Text
from textual.containers import Horizontal, Vertical
from textual.events import Mount
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Label,
    SelectionList,
    Static,
    TabbedContent,
    TabPane,
)
from textual.widgets.selection_list import Selection
from widgets.children_widgets import ChildrenWidget, Input, SearchableChildrenWidget


class ClearFiltersButton(Button):
    pass


class TypeSelection(Selection):
    def __init__(self, prompt, *args, **kwargs):
        super().__init__(prompt, prompt, initial_state=True, *args, **kwargs)


class VisibilitySelection(Selection):
    def __init__(self, prompt, *args, **kwargs):
        super().__init__(prompt, prompt, initial_state=False, *args, **kwargs)


class TypeSelectionList(SelectionList):
    pass


class VisibilitySelectionList(SelectionList):
    pass


class FilterWidget(Static):

    def compose(self):
        with Horizontal() as h:
            h.styles.height = "auto"
            type_list = TypeSelectionList(
                TypeSelection(prompt="class"),
                TypeSelection(prompt="function"),
                TypeSelection(prompt="method"),
                TypeSelection(prompt="module"),
                TypeSelection(prompt="int"),
                TypeSelection(prompt="str"),
                TypeSelection(prompt="float"),
                TypeSelection(prompt="bool"),
                TypeSelection(prompt="list"),
                TypeSelection(prompt="dict"),
                TypeSelection(prompt="set"),
                TypeSelection(prompt="tuple"),
                TypeSelection(prompt="builtin"),
                id="type_list",
            )
            type_list.border_title = "Filter by type"
            type_list.styles.border = ("round", "green")
            yield type_list
            private_list = VisibilitySelectionList(
                VisibilitySelection(prompt="Private"),
                VisibilitySelection(prompt="Dunder"),
            )
            private_list.border_title = "Filter by visibility"
            private_list.styles.border = ("round", "ansi_cyan")
            yield private_list

        yield ClearFiltersButton(label="Clear Filters")

    @textual.on(message_type=ClearFiltersButton.Pressed)
    def on_clear_filters_pressed(self, event: ClearFiltersButton.Pressed):
        self.query_one(selector=VisibilitySelectionList).deselect_all()
        self.query_one(selector=TypeSelectionList).select_all()


class DirectoryWidget(Static):
    def __init__(self, cached_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def compose(self):
        with TabbedContent():
            with TabPane(title="Directory"):
                yield SearchableChildrenWidget(cached_object=self.cached_object)
            with TabPane(title="Filters"):
                yield FilterWidget()

    @textual.on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed):
        if event.checkbox.id == "private":
            self.query_one(ChildrenWidget).show_private = event.checkbox.value
        if event.checkbox.id == "dunder":
            self.query_one(ChildrenWidget).show_dunder = event.checkbox.value

    @textual.on(SelectionList.SelectedChanged)
    def on_selection_list_selected_changed(
        self, event: TypeSelectionList.SelectedChanged
    ):
        self.query_one(ChildrenWidget).type_filters = event.selection_list.selected
