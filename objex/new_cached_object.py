import pydoc
import re
from inspect import (
    cleandoc,
    getdoc,
    getfile,
    getsource,
    isabstract,
    isasyncgen,
    isasyncgenfunction,
    isawaitable,
    isbuiltin,
    isclass,
    iscode,
    iscoroutine,
    iscoroutinefunction,
    isdatadescriptor,
    isfunction,
    isgenerator,
    isgeneratorfunction,
    ismethod,
    ismethoddescriptor,
    ismethodwrapper,
    ismodule,
    isroutine,
    istraceback,
    signature,
)

from rich._inspect import Inspect
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.pretty import Pretty
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
    def __init__(self, obj, name="root"):
        self.obj = obj
        self.name = name
        self.type = type(obj)
        self.type_name = self.type.__name__

        self.cached_children = []

        # Flags
        self.isclass = isclass(obj)
        self.iscallable = callable(obj)
        self.ismodule = ismodule(obj)
        self.ismethod = ismethod(obj)
        self.isfunction = isfunction(obj)
        self.isbuiltin = isbuiltin(obj)
        # Weird types
        self.isabstract = isabstract(obj)
        self.isasyncgen = isasyncgen(obj)
        self.isasyncgenfunction = isasyncgenfunction(obj)
        self.iscoroutine = iscoroutine(obj)
        self.iscoroutinefunction = iscoroutinefunction(obj)
        self.isdatadescriptor = isdatadescriptor(obj)
        self.isgenerator = isgenerator(obj)
        self.isgeneratorfunction = isgeneratorfunction(obj)
        self.ismethoddescriptor = ismethoddescriptor(obj)
        self.ismethodwrapper = ismethodwrapper(obj)
        self.isroutine = isroutine(obj)
        self.istraceback = istraceback(obj)
        self.isawaitable = isawaitable(obj)
        self.iscode = iscode(obj)

        try:
            self.source = getsource(self.obj)  # type: ignore
        except Exception:
            self.source = ""

        # Metadata
        self.inspect = Inspect(obj=obj)

        self.docstring = self.inspect._get_formatted_doc(obj) or ""
        self.help_docs = cleandoc(getdoc(obj) or "")
        if not self.help_docs:
            self.help_docs = re.sub(".\x08", "", pydoc.render_doc(self.obj))

        try:
            self.file = getfile(obj)

        except Exception:
            self.file = None

        try:
            self.signature = signature(obj)
        except Exception:
            self.signature = None

        self.str_data = str(obj)

        # Design
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

    def cache_children(self):
        if self.cached_children:
            return
        for child in sorted(dir(self.obj)):
            try:
                child_obj = getattr(self.obj, child)
                self.cached_children.append(NewCachedObject(obj=child_obj, name=child))
            except:
                pass
