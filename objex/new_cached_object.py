from inspect import cleandoc, getdoc, getfile, isclass, ismodule, signature

from rich._inspect import Inspect
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.pretty import Pretty, pretty_repr
from rich.style import Style
from rich.text import Text

highlighter = ReprHighlighter()
console = Console()


class NewCachedChildObject:
    def __init__(self, obj, name, parent):
        self.obj = obj
        self.name = name
        self.parent = parent
        self.cached_obj = None

        # Flags
        self.isclass = isclass(obj)
        self.iscallable = callable(obj)
        self.ismodule = ismodule(obj)

        # Metadata
        self.inspect = Inspect(obj=obj)
        self.docstring = self.inspect._get_formatted_doc(obj)
        try:
            self.file = getfile(obj)
        except Exception:
            self.file = None
        try:
            self.signature = signature(obj)
        except Exception:
            self.signature = None

        self.str_repr = self._get_str_repr()
        self.style_color = self._get_style_color()
        self.title = self.name
        self.subtitle = self._get_subtitle()

    def _get_str_repr(self):
        signature = self.inspect._get_signature(self.name, self.obj)
        if signature:
            return signature

        pretty = Pretty(self.obj, max_length=1, overflow="ellipsis")
        return pretty

    def _get_style_color(self):
        if self.isclass:
            return "ansi_cyan"

        elif self.iscallable:
            return "ansi_green"

        elif self.ismodule:
            return "ansi_magenta"

        else:
            return "grey"

    def _get_subtitle(self) -> Text:
        name = type(self.obj).__name__
        return Text(text=name)

    def cache(self):
        if self.cached_obj:
            return
        self.cached_obj = NewCachedObject(obj=self.obj)


class NewCachedObject:
    def __init__(self, obj, name=""):
        self.obj = obj
        self.name = name

        self.cached_children = []

        # Flags
        self.isclass = isclass(obj)
        self.iscallable = callable(obj)
        self.ismodule = ismodule(obj)

        # Metadata
        self.inspect = Inspect(obj=obj)
        self.docstring = self.inspect._get_formatted_doc(obj)
        try:
            self.file = getfile(obj)
        except Exception:
            self.file = None
        try:
            self.signature = signature(obj)
        except Exception:
            self.signature = None

        self.str_repr = self._get_str_repr()
        self.style_color = self._get_style_color()
        self.title = self.name
        self.subtitle = self._get_subtitle()

        ##################################
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

    def _get_str_repr(self):
        signature = self.inspect._get_signature(self.name, self.obj)
        if signature:
            return signature

        pretty = Pretty(self.obj, max_length=1, overflow="ellipsis")
        return pretty

    def _get_style_color(self):
        if self.isclass:
            return "ansi_cyan"

        elif self.iscallable:
            return "ansi_green"

        elif self.ismodule:
            return "ansi_magenta"

        else:
            return "grey"

    def _get_subtitle(self) -> Text:
        name = type(self.obj).__name__
        return Text(text=name)

    def cache_children(self):
        self.cached_children = [
            NewCachedObject(obj=getattr(self.obj, child), name=child)
            for child in dir(self.obj)
        ]
