import json
import os

from tree import BinaryTree

SAMPLE_PARTS = [
    ("ENG-401", "1.6L engine block", "Engine", 2, 6500000, "South Auto Parts"),
    ("BRK-202", "Vented brake disc", "Brakes", 18, 260000, "Andean Brakes"),
    ("BOD-102", "Front left door", "Body", 4, 1200000, "Andean Bodyworks"),
    ("BOD-101", "Front hood", "Body", 6, 850000, "Andean Bodyworks"),
    ("BRK-201", "Front brake pads", "Brakes", 40, 145000, "Andean Brakes"),
    ("ELE-301", "12V 60Ah battery", "Electrical", 15, 420000, "ElectroAuto"),
    ("BRK-203", "DOT4 brake fluid", "Brakes", 8, 38000, "Pacific Lubricants"),
    ("ELE-302", "90A alternator", "Electrical", 5, 780000, "ElectroAuto"),
    ("SUS-502", "Rear coil spring", "Suspension", 7, 180000, "Pasto Suspensions"),
    ("ENG-403", "Iridium spark plug", "Engine", 9, 45000, "South Auto Parts"),
    ("ENG-402", "Oil filter", "Engine", 60, 28000, "Pacific Lubricants"),
    ("SUS-501", "Front shock absorber", "Suspension", 12, 310000, "Pasto Suspensions"),
    ("TRN-602", "5-speed manual gearbox", "Transmission", 1, 4800000, "Colombia Transmissions"),
    ("TRN-601", "Clutch kit", "Transmission", 3, 950000, "Colombia Transmissions"),
    ("TRN-603", "75W-90 transmission oil", "Transmission", 25, 52000, "Pacific Lubricants"),
]


def load_sample(tree):
    tree.root = None
    for part in SAMPLE_PARTS:
        tree.insert(*part)
    return tree


def save_tree(tree, path):
    data = [node.to_dict() for node in tree.pre_order()]
    for item in data:
        item.pop("low_stock", None)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tree(path):
    tree = BinaryTree()
    if not os.path.exists(path):
        load_sample(tree)
        save_tree(tree, path)
        return tree
    with open(path, encoding="utf-8") as f:
        for item in json.load(f):
            tree.insert(item["code"], item["name"], item["system"],
                        item["stock"], item["cost"], item["supplier"])
    return tree
