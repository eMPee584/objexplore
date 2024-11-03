from json import tool

import textual
from new_cached_object import NewCachedObject
from rich.text import Text
from textual.containers import Horizontal, HorizontalGroup, Vertical, VerticalGroup
from textual.events import Mount
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Label,
    SelectionList,
    Static,
    Switch,
    TabbedContent,
    TabPane,
)
from textual.widgets.selection_list import Selection
from widgets.children_widgets import ChildrenWidget, SearchableChildrenWidget


class ResetFiltersButton(Button):
    pass


class ClearFiltersButton(Button):
    def on_mount(self):
        self.styles.margin = (0, 1)


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


class FiltersWidget(Static):
    def on_mount(self):
        self.styles.border = ("round", "green")
        self.border_title = "Filters"
        self.styles.border_title_align = "right"

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
            type_list.border_title = "Type"
            type_list.styles.border = ("round", "green")
            yield type_list
            private_list = VisibilitySelectionList(
                VisibilitySelection(prompt="Private"),
                VisibilitySelection(prompt="Dunder"),
            )
            private_list.border_title = "Visibility"
            private_list.styles.border = ("round", "ansi_cyan")
            yield private_list

        with HorizontalGroup() as h:
            yield ResetFiltersButton(label="Reset Filters", id="reset_filters")
            yield ClearFiltersButton(label="Clear Filters", id="clear_filters")

    @textual.on(message_type=Button.Pressed)
    def on_reset_filters_pressed(self, event: Button.Pressed):
        if event.button.id == "reset_filters":
            self.query_one(selector=VisibilitySelectionList).deselect_all()
            self.query_one(selector=TypeSelectionList).select_all()

        elif event.button.id == "clear_filters":
            self.query_one(selector=VisibilitySelectionList).deselect_all()
            self.query_one(selector=TypeSelectionList).deselect_all()


class MyLabel(Label):
    def on_mount(self):
        self.styles.height = 3
        self.styles.padding = (1, 0)
        self.styles.width = "1fr"
        self.styles.text_align = "right"


class SearchOptionsWidget(Static):
    def on_mount(self):
        self.styles.border = ("round", "coral")
        self.border_title = "Search Options"
        self.styles.border_title_align = "right"
        self.styles.height = "auto"

    def compose(self):
        with HorizontalGroup() as h:
            with VerticalGroup() as v:
                label = MyLabel(renderable="Search Help")
                label.tooltip = "Search the help docs for each object"
                yield label
                label = MyLabel(renderable="Fuzzy Search")
                label.tooltip = "Use fuzzy searching"
                yield label
            with VerticalGroup():
                yield Switch(
                    name="Search Help",
                    animate=False,
                    tooltip="Search the help docs for each object",
                    id="help_switch",
                )
                yield Switch(
                    name="Fuzzy Search",
                    value=True,
                    animate=False,
                    id="fuzzy_switch",
                    tooltip="Use fuzzy searching",
                )


class SearchWidget(Static):
    def __init__(self, cached_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def on_mount(self):
        self.styles.border = ("round", "white")
        self.styles.height = "1fr"
        self.border_title = "Search"

    def compose(self):
        with TabbedContent():
            with TabPane(title="Search"):
                yield SearchableChildrenWidget(cached_object=self.cached_object)
            with TabPane(title="Options"):
                yield FiltersWidget()
                yield SearchOptionsWidget()

    @textual.on(message_type=Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed):
        if event.checkbox.id == "private":
            self.query_one(selector=ChildrenWidget).show_private = event.checkbox.value
        if event.checkbox.id == "dunder":
            self.query_one(selector=ChildrenWidget).show_dunder = event.checkbox.value

    @textual.on(message_type=SelectionList.SelectedChanged)
    def on_selection_list_selected_changed(
        self, event: TypeSelectionList.SelectedChanged
    ):
        self.query_one(selector=ChildrenWidget).type_filters = (
            event.selection_list.selected
        )

    @textual.on(message_type=Switch.Changed)
    def on_switch_changed(self, event: Switch.Changed):
        if event.switch.id == "help_switch":
            self.query_one(selector=ChildrenWidget).search_help = event.switch.value

        elif event.switch.id == "fuzzy_switch":
            self.query_one(selector=ChildrenWidget).fuzzy_search = event.switch.value
