import os
import re
import sys

sys.dont_write_bytecode = True

from flask import Flask, jsonify, render_template, request

from assembly import SYSTEMS, build_assembly
from storage import load_sample, load_tree, save_tree

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "inventory.json")
VEHICLE_NAME = "SC-2026 Sedan"
CODE_PATTERN = re.compile(r"^[A-Z0-9]{2,6}-[A-Z0-9]{1,6}$")

app = Flask(__name__, template_folder=BASE_DIR, static_folder=None)
tree = load_tree(DATA_FILE)


def parts_json(nodes):
    return [node.to_dict() for node in nodes]


def normalize_code(code):
    return (code or "").strip().upper()


def snapshot(message=None, **extra):
    data = {
        "tree": tree.to_dict(),
        "stats": tree.stats(),
        "inorder": parts_json(tree.in_order()),
    }
    if message:
        data["message"] = message
    data.update(extra)
    return data


def error(message, status=400):
    return jsonify({"error": message}), status


@app.route("/")
def index():
    return render_template("index.html", systems=SYSTEMS, vehicle=VEHICLE_NAME)


@app.get("/api/tree")
def get_tree():
    return jsonify(snapshot())


@app.post("/api/parts")
def add_part():
    body = request.get_json(silent=True) or {}
    code = normalize_code(body.get("code"))
    name = (body.get("name") or "").strip()
    system = (body.get("system") or "").strip()
    supplier = (body.get("supplier") or "").strip()

    if not CODE_PATTERN.match(code):
        return error("The code must look like SYS-123 (letters/numbers and one dash).")
    if not name:
        return error("The part name is required.")
    if system not in SYSTEMS:
        return error("Select a valid system.")
    if not supplier:
        return error("The supplier is required.")
    try:
        stock = int(body.get("stock"))
        cost = float(body.get("cost"))
    except (TypeError, ValueError):
        return error("Stock and cost must be numbers.")
    if stock < 0 or cost < 0:
        return error("Stock and cost cannot be negative.")
    if cost.is_integer():
        cost = int(cost)

    created = tree.insert(code, name, system, stock, cost, supplier)
    save_tree(tree, DATA_FILE)
    _, path = tree.search_path(code)
    message = f"Part {code} added at level {len(path)}." if created \
        else f"Part {code} already existed: its data was updated."
    return jsonify(snapshot(message, created=created, path=path, code=code))


@app.delete("/api/parts/<code>")
def delete_part(code):
    code = normalize_code(code)
    if not tree.delete(code):
        return error(f"Part {code} does not exist.", 404)
    save_tree(tree, DATA_FILE)
    return jsonify(snapshot(f"Part {code} deleted."))


@app.get("/api/parts/<code>")
def get_part(code):
    code = normalize_code(code)
    node, path = tree.search_path(code)
    if node is None:
        return error(f"Part {code} does not exist.", 404)
    data = node.to_dict()
    data.update({
        "level": len(path),
        "path": path,
        "degree": tree.degree(node),
        "type": tree.node_type(node),
        "left": node.left.code if node.left else None,
        "right": node.right.code if node.right else None,
        "parent": path[-2] if len(path) > 1 else None,
    })
    return jsonify(data)


@app.get("/api/search")
def search():
    query = (request.args.get("q") or "").strip()
    if not query:
        return error("Type a code or a name to search.")

    node, path = tree.search_path(normalize_code(query))
    if node is not None:
        return jsonify({
            "mode": "code",
            "path": path,
            "visited": len(path),
            "total": tree.weight(),
            "results": [node.to_dict()],
        })

    matches = tree.search_by_name(query)
    return jsonify({
        "mode": "name",
        "path": path,
        "visited": tree.weight(),
        "total": tree.weight(),
        "results": parts_json(matches),
    })


@app.get("/api/traversal/<kind>")
def traversal(kind):
    try:
        nodes = tree.traversal(kind)
    except ValueError as exc:
        return error(str(exc))
    return jsonify({"kind": kind, "results": parts_json(nodes)})


@app.get("/api/filter")
def filter_parts():
    def number(name, cast=float):
        value = request.args.get(name, "").strip()
        return cast(value) if value else None

    try:
        nodes = tree.filter(
            system=request.args.get("system") or None,
            supplier=request.args.get("supplier") or None,
            max_stock=number("max_stock", int),
            min_cost=number("min_cost"),
            max_cost=number("max_cost"),
            text=request.args.get("text") or None,
        )
    except ValueError:
        return error("Numeric filters must be numbers.")
    return jsonify({"results": parts_json(nodes)})


@app.get("/api/range")
def code_range():
    low = normalize_code(request.args.get("from"))
    high = normalize_code(request.args.get("to"))
    if not low or not high:
        return error("Enter the start and end codes.")
    if low > high:
        low, high = high, low
    return jsonify({"results": parts_json(tree.range_by_code(low, high))})


@app.get("/api/assembly")
def assembly():
    root = build_assembly(tree, VEHICLE_NAME)
    return jsonify({
        "tree": root.to_dict(),
        "weight": root.weight(),
        "height": root.height(),
        "order": root.order(),
    })


@app.post("/api/balance")
def balance():
    before = tree.height()
    tree.balance()
    save_tree(tree, DATA_FILE)
    return jsonify(snapshot(f"Tree balanced: height {before} → {tree.height()}."))


@app.post("/api/reset")
def reset():
    load_sample(tree)
    save_tree(tree, DATA_FILE)
    return jsonify(snapshot("Sample parts restored."))


if __name__ == "__main__":
    app.run(debug=True)
