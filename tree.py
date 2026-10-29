import unicodedata

LOW_STOCK_THRESHOLD = 5


def _normalize(text):
    text = unicodedata.normalize("NFD", str(text).lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


class Node:
    def __init__(self, code, name, system, stock, cost, supplier):
        self.code = code
        self.name = name
        self.system = system
        self.stock = stock
        self.cost = cost
        self.supplier = supplier
        self.left = None
        self.right = None

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "system": self.system,
            "stock": self.stock,
            "cost": self.cost,
            "supplier": self.supplier,
            "low_stock": self.stock <= LOW_STOCK_THRESHOLD,
        }


class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, code, name, system, stock, cost, supplier):
        new_node = Node(code, name, system, stock, cost, supplier)

        if self.root is None:
            self.root = new_node
            return True

        current = self.root
        while True:
            if code < current.code:
                if current.left is None:
                    current.left = new_node
                    return True
                current = current.left
            elif code > current.code:
                if current.right is None:
                    current.right = new_node
                    return True
                current = current.right
            else:
                current.name = name
                current.system = system
                current.stock = stock
                current.cost = cost
                current.supplier = supplier
                return False

    def search(self, code):
        current = self.root
        while current is not None:
            if code == current.code:
                return current
            elif code < current.code:
                current = current.left
            else:
                current = current.right
        return None

    def search_path(self, code):
        path = []
        current = self.root
        while current is not None:
            path.append(current.code)
            if code == current.code:
                return current, path
            elif code < current.code:
                current = current.left
            else:
                current = current.right
        return None, path

    def search_by_name(self, text):
        text = _normalize(text)
        return [
            node for node in self.in_order()
            if text in _normalize(node.name)
            or text in _normalize(node.code)
            or text in _normalize(node.supplier)
        ]

    def delete(self, code):
        self.root, deleted = self._delete_recursive(self.root, code)
        return deleted

    def _delete_recursive(self, current_node, code):
        if current_node is None:
            return None, False

        if code < current_node.code:
            current_node.left, deleted = self._delete_recursive(current_node.left, code)
            return current_node, deleted
        if code > current_node.code:
            current_node.right, deleted = self._delete_recursive(current_node.right, code)
            return current_node, deleted

        if current_node.left is None:
            return current_node.right, True
        if current_node.right is None:
            return current_node.left, True

        successor = current_node.right
        while successor.left is not None:
            successor = successor.left
        current_node.code = successor.code
        current_node.name = successor.name
        current_node.system = successor.system
        current_node.stock = successor.stock
        current_node.cost = successor.cost
        current_node.supplier = successor.supplier
        current_node.right, _ = self._delete_recursive(current_node.right, successor.code)
        return current_node, True

    def in_order(self):
        result = []
        self._in_order(self.root, result)
        return result

    def _in_order(self, current_node, result):
        if current_node is not None:
            self._in_order(current_node.left, result)
            result.append(current_node)
            self._in_order(current_node.right, result)

    def in_order_desc(self):
        result = []
        self._in_order_desc(self.root, result)
        return result

    def _in_order_desc(self, current_node, result):
        if current_node is not None:
            self._in_order_desc(current_node.right, result)
            result.append(current_node)
            self._in_order_desc(current_node.left, result)

    def pre_order(self):
        result = []
        self._pre_order(self.root, result)
        return result

    def _pre_order(self, current_node, result):
        if current_node is not None:
            result.append(current_node)
            self._pre_order(current_node.left, result)
            self._pre_order(current_node.right, result)

    def post_order(self):
        result = []
        self._post_order(self.root, result)
        return result

    def _post_order(self, current_node, result):
        if current_node is not None:
            self._post_order(current_node.left, result)
            self._post_order(current_node.right, result)
            result.append(current_node)

    def traversal(self, kind):
        kinds = {
            "inorder": self.in_order,
            "inorder_desc": self.in_order_desc,
            "preorder": self.pre_order,
            "postorder": self.post_order,
        }
        if kind not in kinds:
            raise ValueError(f"Unknown traversal: {kind}")
        return kinds[kind]()

    def weight(self):
        return self._weight(self.root)

    def _weight(self, current_node):
        if current_node is None:
            return 0
        return 1 + self._weight(current_node.left) + self._weight(current_node.right)

    def height(self):
        return self._height(self.root)

    def _height(self, current_node):
        if current_node is None:
            return 0
        return 1 + max(self._height(current_node.left), self._height(current_node.right))

    def leaves(self):
        return [n for n in self.in_order() if n.left is None and n.right is None]

    def level_of(self, code):
        node, path = self.search_path(code)
        return len(path) if node else None

    @staticmethod
    def degree(node):
        return (node.left is not None) + (node.right is not None)

    def node_type(self, node):
        if node is self.root:
            return "root"
        if node.left is None and node.right is None:
            return "leaf"
        return "branch"

    def min_node(self):
        current = self.root
        while current is not None and current.left is not None:
            current = current.left
        return current

    def max_node(self):
        current = self.root
        while current is not None and current.right is not None:
            current = current.right
        return current

    def stats(self):
        parts = self.in_order()
        low = [p for p in parts if p.stock <= LOW_STOCK_THRESHOLD]
        min_node, max_node = self.min_node(), self.max_node()
        return {
            "weight": len(parts),
            "height": self.height(),
            "leaves": len(self.leaves()),
            "order": 2,
            "root": self.root.code if self.root else None,
            "min_code": min_node.code if min_node else None,
            "max_code": max_node.code if max_node else None,
            "total_units": sum(p.stock for p in parts),
            "inventory_value": sum(p.stock * p.cost for p in parts),
            "low_stock": len(low),
            "low_stock_threshold": LOW_STOCK_THRESHOLD,
        }

    def filter(self, system=None, supplier=None, max_stock=None,
               min_cost=None, max_cost=None, text=None):
        result = []
        for node in self.in_order():
            if system and node.system != system:
                continue
            if supplier and _normalize(supplier) not in _normalize(node.supplier):
                continue
            if max_stock is not None and node.stock > max_stock:
                continue
            if min_cost is not None and node.cost < min_cost:
                continue
            if max_cost is not None and node.cost > max_cost:
                continue
            if text and _normalize(text) not in _normalize(node.name) \
                    and _normalize(text) not in _normalize(node.code):
                continue
            result.append(node)
        return result

    def range_by_code(self, low, high):
        result = []
        self._range(self.root, low, high, result)
        return result

    def _range(self, current_node, low, high, result):
        if current_node is None:
            return
        if low < current_node.code:
            self._range(current_node.left, low, high, result)
        if low <= current_node.code <= high:
            result.append(current_node)
        if current_node.code < high:
            self._range(current_node.right, low, high, result)

    def balance(self):
        parts = self.in_order()
        self.root = None
        self._insert_middle(parts, 0, len(parts) - 1)

    def _insert_middle(self, parts, start, end):
        if start > end:
            return
        middle = (start + end) // 2
        p = parts[middle]
        self.insert(p.code, p.name, p.system, p.stock, p.cost, p.supplier)
        self._insert_middle(parts, start, middle - 1)
        self._insert_middle(parts, middle + 1, end)

    def to_dict(self):
        return self._node_dict(self.root, 1)

    def _node_dict(self, node, level):
        if node is None:
            return None
        data = node.to_dict()
        data.update({
            "level": level,
            "degree": self.degree(node),
            "type": self.node_type(node),
            "left": self._node_dict(node.left, level + 1),
            "right": self._node_dict(node.right, level + 1),
        })
        return data
