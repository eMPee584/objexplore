import textual
from new_cached_object import NewCachedObject
from rich.text import Text
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.events import Mount
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Label,
    Select,
    SelectionList,
    Static,
    Switch,
    TabbedContent,
    TabPane,
)
from textual.widgets.selection_list import Selection
from widgets.children import ChildrenWidget, SearchableChildrenWidget


class ResetFiltersButton(Button):
    def on_mount(self):
        self.styles.margin = (0, 1)


class ClearFiltersButton(Button):
    def on_mount(self):
        self.styles.margin = (0, 1)


class ShowAllButton(Button):
    def on_mount(self):
        self.styles.margin = (0, 1)


class TypeSelection(Selection):
    def __init__(self, prompt, *args, **kwargs):
        super().__init__(prompt, prompt, initial_state=True, *args, **kwargs)


class VisibilitySelection(Selection):
    def __init__(self, prompt, *args, **kwargs):
        super().__init__(prompt, prompt, initial_state=True, *args, **kwargs)


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
                VisibilitySelection(prompt="private"),
                VisibilitySelection(prompt="dunder"),
                id="visibility_list",
            )
            private_list.tooltip = "Show private attributes (beginning with _) or dunder attributes (beginning with __)"
            private_list.border_title = "Visibility"
            private_list.styles.border = ("round", "ansi_cyan")
            yield private_list

        with HorizontalGroup() as h:
            yield ShowAllButton(label="Select All", id="select_all", variant="primary")
            yield ClearFiltersButton(label="Clear Filters", id="clear_filters")

    @textual.on(message_type=Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "select_all":
            self.query_one(selector=VisibilitySelectionList).select_all()
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
                label = MyLabel(renderable="Fuzzy Search")
                label.tooltip = "Use fuzzy searching"
                yield label
                label = MyLabel(renderable="Search Help")
                label.tooltip = "Search the help docs for each object"
                yield label
                label = MyLabel(renderable="Search Data")
                label.tooltip = "Search within a str() representation of the object"
                yield label
                label = MyLabel(renderable="Sort by")
                label.tooltip = "Choose how to sort the results"
                yield label

            with VerticalGroup():
                yield Switch(
                    name="Fuzzy Search",
                    value=True,
                    animate=False,
                    id="fuzzy_switch",
                    tooltip="Use fuzzy searching",
                )
                yield Switch(
                    name="Search Help",
                    animate=False,
                    tooltip="Search the help docs for each object",
                    id="help_switch",
                )
                yield Switch(
                    name="Search Data",
                    animate=False,
                    tooltip="Search within a str() representation of the object",
                    id="data_switch",
                )
                select = Select(
                    prompt="Sort by",
                    options=[("Name", "name"), ("Type", "type")],
                    value="name",
                    allow_blank=False,
                    tooltip="Choose how to sort the results",
                    id="sort_by",
                )
                select.styles.width = 20
                yield select


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
                with VerticalScroll():
                    yield FiltersWidget()
                    yield SearchOptionsWidget()

    @textual.on(message_type=SelectionList.SelectedChanged)
    def on_selection_list_selected_changed(
        self, event: TypeSelectionList.SelectedChanged
    ):
        if event.selection_list.id == "type_list":
            self.query_one(selector=ChildrenWidget).type_filters = (
                event.selection_list.selected
            )
        elif event.selection_list.id == "visibility_list":
            self.query_one(selector=ChildrenWidget).visibility_filters = (
                event.selection_list.selected
            )

    @textual.on(message_type=Switch.Changed)
    def on_switch_changed(self, event: Switch.Changed):
        if event.switch.id == "help_switch":
            self.query_one(selector=ChildrenWidget).search_help = event.switch.value

        elif event.switch.id == "fuzzy_switch":
            self.query_one(selector=ChildrenWidget).fuzzy_search = event.switch.value

    @textual.on(message_type=Select.Changed)
    def on_select_changed(self, event: Select.Changed):
        if event.select.id == "sort_by":
            self.query_one(selector=ChildrenWidget).sort_by = event.value
