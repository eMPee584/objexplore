class NewCachedChildObject:
    def __init__(self, obj, label, parent):
        self.obj = obj
        self.label = label
        self.parent = parent


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
