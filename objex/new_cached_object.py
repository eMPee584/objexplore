from inspect import cleandoc, getdoc, getfile, isclass, ismodule, signature

from rich.highlighter import ReprHighlighter
from rich.style import Style
from rich.text import Text

highlighter = ReprHighlighter()


class NewCachedChildObject:
    def __init__(self, obj, label, parent):
        self.obj = obj
        self.label = label
        self.parent = parent
        self.cached_obj = None

        # Flags
        self.is_class = isclass(obj)
        self.is_callable = callable(obj)
        self.is_module = ismodule(obj)

        if self.is_class:
            self.style = Style(color="blue")
            self.title_str = Text("class", style=self.style)

        elif self.is_callable:
            self.style = Style(color="green")
            self.title_str = Text("callable", style=self.style)

        elif self.is_module:
            self.style = Style(color="cyan")
            self.title_str = Text("module", style=self.style)

        else:
            self.style = Style(color="white")
            self.title_str = Text("object", style=self.style)

    def cache(self):
        if self.cached_obj:
            return
        self.cached_obj = NewCachedObject(self.obj)


class NewCachedObject:
    def __init__(self, obj):
        self.obj = obj

        self.all_children = [
            NewCachedChildObject(getattr(obj, child_label), child_label, self)
            for child_label in dir(obj)
        ]
        self.public_children = [
            child for child in self.all_children if not child.label.startswith("_")
        ]
        self.private_children = [
            child for child in self.all_children if child.label.startswith("_")
        ]
