from inspect import cleandoc, getdoc, getfile, isclass, ismodule, signature

from rich.highlighter import ReprHighlighter
from rich.style import Style
from rich.text import Text

highlighter = ReprHighlighter()


class NewCachedChildObject:
    def __init__(self, obj, name, parent):
        self.obj = obj
        self.name = name
        self.parent = parent
        self.cached_obj = None

        # Flags
        self.is_class = isclass(obj)
        self.is_callable = callable(obj)
        self.is_module = ismodule(obj)

        # Metadata
        self.docstring = getdoc(obj)
        # self.file = getfile(obj)
        try:
            self.signature = signature(obj)
        except Exception:
            self.signature = None

        self.style = self._get_style()
        self.title = self._get_title()

    def _get_style(self):
        if self.is_class:
            return Style(color="cyan")

        elif self.is_callable:
            return Style(color="green")

        elif self.is_module:
            return Style(color="blue")

        else:
            return Style(color="white")

    def _get_title(self) -> Text:
        name = type(self.obj).__name__
        return Text(text=name, style=self.style)

    def cache(self):
        if self.cached_obj:
            return
        self.cached_obj = NewCachedObject(obj=self.obj)


class NewCachedObject:
    def __init__(self, obj):
        self.obj = obj

        self.all_children = [
            NewCachedChildObject(getattr(obj, child_label), child_label, self)
            for child_label in dir(obj)
        ]
        self.public_children = [
            child for child in self.all_children if not child.name.startswith("_")
        ]
        self.private_children = [
            child for child in self.all_children if child.name.startswith("_")
        ]
