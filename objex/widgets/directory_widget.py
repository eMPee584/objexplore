from new_cached_object import NewCachedObject
from rich.text import Text
from textual.events import Mount
from textual.widgets import Static, TabbedContent, TabPane
from widgets.children_widgets import SearchableChildrenWidget


class DirectoryWidget(Static):
    def __init__(self, cached_object: NewCachedObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_object = cached_object

    def _on_mount(self, event: Mount) -> None:
        self.styles.border = ("round", "white")
        self.border_title = Text.from_markup("[cyan][i]dir[/cyan][white]()")
        self.styles.border_title_align = "right"

    def compose(self):
        yield SearchableChildrenWidget(cached_object=self.cached_object)
