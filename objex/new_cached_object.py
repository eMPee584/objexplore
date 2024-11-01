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

        self.str_repr = self._get_str_repr()
        self.style, self.style_color = self._get_style()
        self.title = self.name
        self.subtitle = self._get_subtitle()

    def _get_str_repr(self):
        return highlighter(repr(self.obj))

    def _get_style(self):
        if self.is_class:
            return Style(color="cyan"), "ansi_cyan"

        elif self.is_callable:
            return Style(color="green"), "ansi_green"

        elif self.is_module:
            return Style(color="blue"), "ansi_magenta"

        else:
            return Style(color="white"), "ansi_white"

    def _get_subtitle(self) -> Text:
        name = type(self.obj).__name__
        return Text(text=name)

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
