SYSTEMS = ["Engine", "Transmission", "Suspension", "Brakes", "Body", "Electrical"]


class AssemblyNode:
    def __init__(self, name, kind, part=None):
        self.name = name
        self.kind = kind
        self.part = part
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return child

    def weight(self):
        return 1 + sum(child.weight() for child in self.children)

    def height(self):
        return 1 + max((child.height() for child in self.children), default=0)

    def order(self):
        return max([len(self.children)] + [child.order() for child in self.children])

    def total_cost(self):
        if self.part is not None:
            return self.part.stock * self.part.cost
        return sum(child.total_cost() for child in self.children)

    def count_parts(self):
        if self.part is not None:
            return 1
        return sum(child.count_parts() for child in self.children)

    def to_dict(self):
        data = {
            "name": self.name,
            "kind": self.kind,
            "degree": len(self.children),
            "parts": self.count_parts(),
            "total_cost": self.total_cost(),
            "children": [child.to_dict() for child in self.children],
        }
        if self.part is not None:
            data["part"] = self.part.to_dict()
        return data


def build_assembly(tree, vehicle_name):
    root = AssemblyNode(vehicle_name, "vehicle")
    systems = {name: root.add_child(AssemblyNode(name, "system")) for name in SYSTEMS}

    for node in tree.in_order():
        if node.system not in systems:
            systems[node.system] = root.add_child(AssemblyNode(node.system, "system"))
        systems[node.system].add_child(AssemblyNode(node.name, "part", node))

    return root
