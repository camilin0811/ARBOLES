import sys
import unittest

sys.dont_write_bytecode = True

from assembly import build_assembly
from storage import load_sample
from tree import BinaryTree


def codes(nodes):
    return [n.code for n in nodes]


class TestBinaryTree(unittest.TestCase):
    def setUp(self):
        self.tree = load_sample(BinaryTree())

    def test_inorder_sorted(self):
        result = codes(self.tree.in_order())
        self.assertEqual(result, sorted(result))
        self.assertEqual(codes(self.tree.in_order_desc()), sorted(result, reverse=True))

    def test_weight_height_leaves(self):
        self.assertEqual(self.tree.weight(), 15)
        self.assertEqual(self.tree.height(), 4)
        self.assertEqual(len(self.tree.leaves()), 8)

    def test_preorder_rebuilds_same_shape(self):
        copy = BinaryTree()
        for n in self.tree.pre_order():
            copy.insert(n.code, n.name, n.system, n.stock, n.cost, n.supplier)
        self.assertEqual(codes(copy.pre_order()), codes(self.tree.pre_order()))

    def test_search_and_path(self):
        node, path = self.tree.search_path("BRK-203")
        self.assertEqual(node.name, "DOT4 brake fluid")
        self.assertEqual(path, ["ENG-401", "BRK-202", "ELE-301", "BRK-203"])
        self.assertIsNone(self.tree.search("XXX-000"))
        self.assertEqual(self.tree.level_of("ENG-401"), 1)

    def test_insert_duplicate_updates(self):
        created = self.tree.insert("ENG-402", "Premium oil filter", "Engine", 3, 30000, "Other")
        self.assertFalse(created)
        self.assertEqual(self.tree.weight(), 15)
        self.assertEqual(self.tree.search("ENG-402").stock, 3)

    def test_delete_three_cases(self):
        self.assertTrue(self.tree.delete("BOD-101"))
        self.tree.insert("BRK-204", "x", "Brakes", 1, 1, "y")
        self.assertTrue(self.tree.delete("BRK-203"))
        self.assertTrue(self.tree.delete("ENG-401"))
        self.assertFalse(self.tree.delete("ENG-401"))
        self.assertEqual(self.tree.root.code, "ENG-402")
        result = codes(self.tree.in_order())
        self.assertEqual(result, sorted(result))
        self.assertEqual(self.tree.weight(), 13)

    def test_search_by_name_is_case_insensitive(self):
        self.assertEqual(codes(self.tree.search_by_name("SPARK")), ["ENG-403"])

    def test_filter_and_range(self):
        self.assertEqual(codes(self.tree.filter(system="Brakes")), ["BRK-201", "BRK-202", "BRK-203"])
        self.assertEqual(codes(self.tree.filter(max_stock=3)), ["ENG-401", "TRN-601", "TRN-602"])
        self.assertEqual(codes(self.tree.range_by_code("BRK-000", "BRK-999")), ["BRK-201", "BRK-202", "BRK-203"])

    def test_balance(self):
        tree = BinaryTree()
        for i in range(1, 16):
            tree.insert(f"P-{i:03}", "p", "Engine", 1, 1, "s")
        self.assertEqual(tree.height(), 15)
        tree.balance()
        self.assertEqual(tree.height(), 4)
        self.assertEqual(tree.weight(), 15)

    def test_empty_tree(self):
        tree = BinaryTree()
        self.assertEqual(tree.weight(), 0)
        self.assertEqual(tree.height(), 0)
        self.assertIsNone(tree.to_dict())
        self.assertIsNone(tree.stats()["root"])


class TestAssembly(unittest.TestCase):
    def test_assembly_tree(self):
        root = build_assembly(load_sample(BinaryTree()), "Sedan")
        self.assertEqual(root.count_parts(), 15)
        self.assertEqual(root.weight(), 1 + 6 + 15)
        self.assertEqual(root.height(), 3)
        self.assertEqual(root.order(), 6)


if __name__ == "__main__":
    unittest.main()
