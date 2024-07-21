import inspect
from typing import Any, Optional

from directory_panel import ChildWidget, Input
from rich.style import Style
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Label, Pretty, Static, Switch


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
                    parent_object=self.selected_object, child_label=child_label
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
