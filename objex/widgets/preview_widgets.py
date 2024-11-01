from typing import Any, Optional

import rich
from new_cached_object import NewCachedChildObject
from rich._inspect import Inspect
from rich.panel import Panel
from rich.style import Style
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Label, Pretty, Static, Switch


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
) -> Inspect:
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


class InspectWidget(Static):
    def __init__(self, obj, **kwargs):
        super().__init__(renderable=get_inspect(obj), **kwargs)
        self.obj = obj


class DocstringWidget(Static):
    def __init__(self, docstring: Optional[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.docstring = docstring
        self.expanded = False

    def render(self) -> Panel:
        if not self.expanded or (
            self.docstring and len(self.docstring.split("\n")) > 1
        ):
            return Panel(
                renderable=self.docstring or "None",
                height=5,
                title="[green bold italic]docstring",
                title_align="left",
            )
        else:
            return Panel(renderable=self.docstring or "None")


class InspectedObjectWidget(Static):
    DEFAULT_CSS = """
    #pretty {
        background: $primary-background-darken-1;
        border: wide black;
    }
    """
    selected_object_label = reactive(default="")
    selected_object: reactive[Optional[NewCachedChildObject]] = reactive(
        default=None, recompose=True
    )

    def compose(self):
        if self.selected_object:
            with VerticalScroll() as v:
                v.styles.border = ("round", self.selected_object.style_color)
                v.border_title = self.selected_object.name
                yield DocstringWidget(docstring=self.selected_object.docstring)
                yield InspectWidget(obj=self.selected_object.obj)
