from typing import Any, Optional

import rich
from new_cached_object import NewCachedChildObject, NewCachedObject
from rich._inspect import Inspect
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual.containers import Horizontal, HorizontalGroup, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Label, Markdown, Pretty, Static, Switch


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
    expanded = reactive(True, layout=True)

    def __init__(self, cached_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def compose(self):
        if self.expanded:
            renderable = self.cached_object.help_docs
        else:
            renderable = self.cached_object.docstring

        if renderable:
            yield Markdown(markdown=renderable)


class InspectedObjectWidget(Static):
    selected_object_label = reactive(default="")
    selected_object: reactive[Optional[NewCachedObject]] = reactive(
        default=None, recompose=True
    )
    preview_object: reactive[Optional[NewCachedObject]] = reactive(
        default=None, recompose=True
    )

    def __init__(self, selected_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_object = selected_object

    def compose(self):
        if self.preview_object:
            viewing_object = self.preview_object
        else:
            viewing_object = self.selected_object

        if viewing_object:
            with VerticalScroll() as v:
                v.styles.border = ("round", viewing_object.style_color)
                v.border_title = Text(viewing_object.name)
                with VerticalScroll() as v2:
                    v2.styles.max_height = 20
                    v2.styles.border = ("round", "green")
                    v2.border_title = "docstring"
                    v2.styles.height = "auto"
                    yield DocstringWidget(cached_object=viewing_object)

                yield Pretty(viewing_object.obj)
                # yield InspectWidget(obj=viewing_object.obj)


class BreadCrumbObjectWidget(Static):
    DEFAULT_CSS = """
    BreadCrumbObjectWidget {
        &:hover {
            background: $primary-background-darken-1;
            text-style: underline;
        }
    }
    """

    def __init__(self, cached_object: NewCachedObject, index: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object
        self.index = index

    def on_mount(self):
        self.styles.width = "auto"
        self.styles.color = self.cached_object.style_color

    def render(self):
        return Text(self.cached_object.name, style=self.cached_object.style_color)

    def on_click(self, event):
        self.app.pop_to_index(self.index)


class BreadCrumbsWidget(Static):

    def on_mount(self):
        self.styles.border = ("round", "cyan")
        self.border_title = "breadcrumbs"
        self.styles.border_title_color = "white"

    def compose(self):
        with HorizontalGroup() as h:
            for index, cached_object in enumerate(self.app.cached_object_stack):  # type: ignore
                yield BreadCrumbObjectWidget(cached_object=cached_object, index=index)
                yield Label(" > ")


class PreviewWidget(Static):
    def __init__(self, cached_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def compose(self):
        yield BreadCrumbsWidget()
        yield InspectedObjectWidget(selected_object=self.cached_object)
