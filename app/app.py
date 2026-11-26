"""A small Flask REST API used to demo a CI/CD pipeline to AWS EC2."""
import os

from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)

    # In-memory store (fine for a demo; resets on restart).
    items = {}
    state = {"next_id": 1}

    @app.get("/")
    def index():
        return jsonify(
            message="Hello Sai , Party less , work more",
            version=os.getenv("APP_VERSION", "local"),
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/api/items")
    def list_items():
        return jsonify(list(items.values()))

    @app.get("/api/items/<int:item_id>")
    def get_item(item_id):
        item = items.get(item_id)
        if item is None:
            return jsonify(error="Item not found"), 404
        return jsonify(item)

    @app.post("/api/items")
    def create_item():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        if not name or not isinstance(name, str):
            return jsonify(error="'name' is required and must be a string"), 400
        item = {"id": state["next_id"], "name": name}
        items[item["id"]] = item
        state["next_id"] += 1
        return jsonify(item), 201

    @app.put("/api/items/<int:item_id>")
    def update_item(item_id):
        if item_id not in items:
            return jsonify(error="Item not found"), 404
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        if not name or not isinstance(name, str):
            return jsonify(error="'name' is required and must be a string"), 400
        items[item_id]["name"] = name
        return jsonify(items[item_id])

    @app.delete("/api/items/<int:item_id>")
    def delete_item(item_id):
        if items.pop(item_id, None) is None:
            return jsonify(error="Item not found"), 404
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
