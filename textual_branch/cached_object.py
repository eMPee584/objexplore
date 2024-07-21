import inspect

from textual.widgets.option_list import Option


class CachedObject:
    def __init__(self, obj):
        self.obj = obj

        self.children_labels = dir(obj)
        self.children = {
            label: getattr(self.obj, label) for label in self.children_labels
        }

        self.public_children_labels = [
            label for label in dir(obj) if not label.startswith("_")
        ]

        self.private_children_labels = [
            label for label in dir(obj) if label.startswith("_")
        ]

        self.cached_children = {}

    def cache(self):
        self.cached_children = {
            label: CachedObject(child) for label, child in self.children.items()
        }

        self.public_children_options = {
            label: self.get_option_for_child(label)
            for label in self.public_children_labels
        }
        self.private_children_options = {
            label: self.get_option_for_child(label)
            for label in self.private_children_labels
        }

    def get_public_children_options(self, search_query):
        return [
            option
            for label, option in self.public_children_options.items()
            if search_query.lower() in label.lower()
        ]

    def get_private_children_options(self, search_query):
        return [
            option
            for label, option in self.private_children_options.items()
            if search_query.lower() in label.lower()
        ]

    def get_option_for_child(self, child_label):
        child_object = getattr(self.obj, child_label)

        if child_object is None:
            return Option(f"[strike][dim]{child_label}[/]", id=child_label)

        elif inspect.isclass(child_object):
            return Option(f"[magenta]{child_label}[/]", id=child_label)

        elif inspect.ismodule(child_object):
            return Option(f"[blue]{child_label}[/]", id=child_label)

        elif inspect.ismethod(child_object) or inspect.isfunction(child_object):
            return Option(f"[cyan]{child_label}[/cyan]()", id=child_label)

        elif isinstance(child_object, dict):
            return Option("{**[cyan]" + child_label + "[/]}", id=child_label)

        elif isinstance(child_object, bool):
            color = "green" if child_object else "red"
            return Option(
                f"{child_label} = [{color}][i]{child_object}[/i][/{color}]",
                id=child_label,
            )

        elif isinstance(child_object, str):
            return Option(
                f"{child_label} = [green][i]'{child_object}'[/i][/green]",
                id=child_label,
            )

        elif isinstance(child_object, list):
            return Option(
                "[*" + f"[red]{child_label}[/red]" + "]",
                id=child_label,
            )

        return Option(child_label, id=child_label)
