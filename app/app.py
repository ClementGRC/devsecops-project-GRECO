"""
DevSecOps Project - Flask API
Simple REST API for security pipeline demonstration.
"""

from flask import Flask, jsonify, request, render_template_string
import os
import logging

app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# In-memory storage
ITEMS = [
    {"id": 1, "name": "Pipeline CI/CD", "category": "devops"},
    {"id": 2, "name": "Trivy Scanner", "category": "security"},
    {"id": 3, "name": "Conftest OPA", "category": "policy"},
    {"id": 4, "name": "Hadolint", "category": "linting"},
]


@app.route("/")
def index():
    """Root endpoint - returns app info."""
    return jsonify({
        "application": "devsecops-api",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/", "/health", "/items", "/items/<id>", "/info"],
    })


@app.route("/health")
def health():
    """Health check endpoint for Kubernetes probes."""
    return jsonify({"status": "healthy"}), 200


@app.route("/info")
def info():
    """Returns runtime information."""
    return jsonify({
        "environment": os.environ.get("FLASK_ENV", "production"),
        "python_version": os.environ.get("PYTHON_VERSION", "3.11"),
        "debug_mode": app.config["DEBUG"],
    })


@app.route("/items", methods=["GET"])
def list_items():
    """Returns all items, optional filter by category."""
    category = request.args.get("category")
    if category:
        filtered = [i for i in ITEMS if i["category"] == category]
        return jsonify({"count": len(filtered), "items": filtered})
    return jsonify({"count": len(ITEMS), "items": ITEMS})


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Returns a single item by ID."""
    item = next((i for i in ITEMS if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.route("/items", methods=["POST"])
def create_item():
    """Creates a new item."""
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        return jsonify({"error": "Missing 'name' field"}), 400

    new_item = {
        "id": max(i["id"] for i in ITEMS) + 1,
        "name": data["name"],
        "category": data.get("category", "uncategorized"),
    }
    ITEMS.append(new_item)
    logger.info("Item created: %s", new_item["name"])
    return jsonify(new_item), 201


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
