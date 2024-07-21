import inspect
from typing import Any, Optional

import textual
from common_widgets import Input
from rich.pretty import Pretty as RichPretty
from rich.style import Style
from rich.table import Table
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import DataTable, Label, Pretty, Static, Switch

from objexplore.cached_object import CachedObject

# class ChildWidget(Static):

#     def __init__(self, parent_object, child_label, *args, **kwargs):
#         self.parent_object = parent_object
#         self.child_label = child_label
#         super().__init__(*args, **kwargs)

#     def on_mount(self):
#         self.styles.height = "auto"

#     def compose(self):
#         table = DataTable(show_header=False)
#         table.add_column("Attribute")
#         table.add_column("Value")
#         table.add_row(
#             self.child_label,
#             RichPretty(
#                 getattr(self.parent_object, self.child_label),
#                 overflow="ellipsis",
#                 max_length=2,
#             ),
#         )

#         yield table


class ModuleClassPreviewWidget(Static):
    search_query = reactive("", recompose=True)

    def __init__(self, selected_object, *args, **kwargs):
        # TODO make selected object a cached object
        self.selected_object = selected_object
        super().__init__(*args, **kwargs)

    def compose(self):
        table = DataTable(cursor_type="row")
        table.styles.text_align = "center"
        table.styles.margin = (1, 0)
        table.add_column("Attribute")
        table.add_column("Value")
        for child_label in dir(self.selected_object):
            if not self.search_query.lower() in child_label.lower():
                continue

            table.add_row(
                child_label,
                RichPretty(
                    getattr(self.selected_object, child_label),
                    overflow="ellipsis",
                    max_length=2,
                ),
                height=3,
            )
        yield table


class PreviewWidget(Static):

    def __init__(self, cached_object, *args, **kwargs):
        self.cached_object = cached_object
        super().__init__(*args, **kwargs)

    @property
    def selected_object(self):
        return self.cached_object.obj

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
            yield ModuleClassPreviewWidget(self.selected_object)

    @textual.on(Input.Changed)  # type: ignore
    def update_search_query(self, event: Input.Changed):
        self.query_one(ModuleClassPreviewWidget).search_query = event.value


class InspectedObjectWidget(Static):
    DEFAULT_CSS = """
    #pretty {
        background: $primary-background-darken-1;
        border: wide black;
    }
    """
    selected_object_label = reactive("")
    cached_object = reactive(CachedObject(None), recompose=True)

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
                _type = Pretty(type(self.cached_object.obj))
                _type.styles.border = ("round", "cyan")
                _type.border_title = "Type"
                _type.styles.border_title_color = "white"
                _type.styles.border_title_style = Style(italic=True)
                yield _type

        yield PreviewWidget(cached_object=self.cached_object)


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
