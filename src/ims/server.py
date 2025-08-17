from flask import Flask, jsonify, request

app = Flask(__name__)

# in-memory database

# list of item dicts
_DB = []
# auto-increment id for new items
_NEXT_ID = 1

# API health check: GET /api/health
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

# CRUD: /api/items
# Internal schema
#   id                int (generated)
#   product_name      str (required)
#   barcode           str (required)
#   product_quantity  int (default = 0)

# return all items
@app.get("/api/items")
def list_items():
    return jsonify(_DB), 200

# create a new item
@app.post("/api/items")
def create_item():
    global _NEXT_ID
    data = request.get_json(silent=True) or {}

    # validation for the call, product_name and barcode required
    if "product_name" not in data or "barcode" not in data:
        return jsonify({"error": "product_name and barcode are required"}), 400

    item = {
        "id": _NEXT_ID,
        "product_name": data.get("product_name"),
        "barcode": data.get("barcode"),
        # Coerce numeric inputs; default to 0 if missing/blank
        "product_quantity": int(data.get("product_quantity", 0) or 0),
        "price_cents": int(data.get("price_cents", 0) or 0),
    }

    _NEXT_ID += 1
    _DB.append(item)
    return jsonify(item), 201

# fetch an item by id
@app.get("/api/items/<int:item_id>")
def get_item(item_id: int):
    for it in _DB:
        if it["id"] == item_id:
            return jsonify(it), 200
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# partially update an item, only for known fields and ignore any unknown key (to support clients sending extra data without breaking)
@app.patch("/api/items/<int:item_id>")
def update_item(item_id: int):
    payload = request.get_json(silent=True) or {}

    for it in _DB:
        if it["id"] == item_id:
            # only allow updates to known fields
            for key in ("product_name", "barcode", "product_quantity"):
                if key in payload:
                    # Normalize numeric types for consistency
                    if key in ("product_quantity"):
                        it[key] = int(payload[key])
                    else:
                        it[key] = payload[key]
            return jsonify(it), 200
    
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# delete item by id
@app.delete("/api/items/<int:item_id>")
def delete_item(item_id: int):
    global _DB
    before = len(_DB)
    
    _DB = [x for x in _DB if x["id"] != item_id]

    if len(_DB) < before:
        # return {deleted: <id>} if successful
        return jsonify({"deleted": item_id}), 200
    
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# Helper routes for /restock and /deduct
# delta = how much to add or remove
# 
# delta           int (required, must be >= 0)
# deduct          int (never goes below 0 / clamp behavior)

def _parse_delta(payload):
    
    # validation that the 'delta' field is present and return the delta_int otherwise return error response or none
    
    if payload is None:
        return None, (jsonify({"error": "JSON body required"}), 400)
    if "delta" not in payload:
        return None, (jsonify({"error": "delta is required"}), 400)
    
    # Must be an integer (e.g., 5, "5" --> 5; but "abc" --> error)
    try:
        delta = int(payload["delta"])
    except (TypeError, ValueError):
        return None, (jsonify({"error": "delta must be an integer"}), 400)
    
    # Must be non-negative
    if delta < 0:
        return None, (jsonify({"error": "delta must be non-negative"}), 400)
    return delta, None

# restock route
@app.post("/api/items/<int:item_id>/restock")
def restock(item_id: int):
    """Add 'delta' to product_quantity."""
    payload = request.get_json(silent=True)
    delta, err = _parse_delta(payload)
    if err:
        return err

    for item in _DB:
        if item["id"] == item_id:
            item["product_quantity"] = int(item.get("product_quantity", 0)) + delta
            return jsonify(item), 200
    
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# deduct route
@app.post("/api/items/<int:item_id>/deduct")
def deduct(item_id: int):
    """Subtract 'delta' from product_quantity. Never below 0 (clamp)."""
    payload = request.get_json(silent=True)
    delta, err = _parse_delta(payload)
    if err:
        return err

    for item in _DB:
        if item["id"] == item_id:
            new_qty = int(item.get("product_quantity", 0)) - delta
            # clamp at 0 so quantity is never negative
            item["product_quantity"] = new_qty if new_qty > 0 else 0
            return jsonify(item), 200

    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
