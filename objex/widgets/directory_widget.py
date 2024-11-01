from new_cached_object import NewCachedObject
from textual.widgets import Static, TabbedContent, TabPane
from widgets.children_widgets import PrivateChildrenWidget, PublicChildrenWidget


class DirectoryWidget(Static):
    def __init__(self, cached_obj: NewCachedObject, *args, **kwargs):
        self.cached_obj = cached_obj
        super().__init__(*args, **kwargs)

    def compose(self):
        with TabbedContent():
            with TabPane(title="Public", id="public"):
                yield PublicChildrenWidget(cached_obj=self.cached_obj)

            with TabPane(title="Private", id="private"):
                yield PrivateChildrenWidget(cached_obj=self.cached_obj)
